from aiogram.types import Message
from src.ai.router import extract_entities, extract_inbox
from src.bot.handlers.utils import log_tokens
async def _handle_create_entities(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Habit
    extraction, tokens = extract_entities(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or (not extraction.projects and not extraction.habits):
        await message.answer("I could not determine the exact details for the project or habit to create.")
        return
        
    responses = []
    
    for p in extraction.projects:
        proj = Project(user_id=user.id, title=p.title, status="active", target_value=p.target_value)
        db.add(proj)
        db.flush()
        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        responses.append(msg)
        
    for h in extraction.habits:
        habit = Habit(user_id=user.id, title=h.title, target_value=h.target_value, type="counter")
        db.add(habit)
        db.flush()
        responses.append(f"✅ Habit created: <b>{habit.title}</b>")
        
    db.commit()
    await message.answer("\n".join(responses), parse_mode="HTML")


async def _handle_add_inbox(message: Message, db, user, provider_name, api_key):
    from src.db.models import Inbox
    from src.bot.handlers.utils import log_tokens
    
    extraction, tokens = extract_inbox(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not getattr(extraction, "raw_content", None):
        await message.answer("I could not determine what to save to your inbox.")
        return
        
    inbox_item = Inbox(user_id=user.id, raw_text=extraction.raw_content, status="pending")
    db.add(inbox_item)
    db.commit()
    
    import html
    safe_text = html.escape(extraction.raw_content)
    await message.answer(f"📥 <b>Saved to Inbox:</b>\n<i>{safe_text}</i>", parse_mode="HTML")


