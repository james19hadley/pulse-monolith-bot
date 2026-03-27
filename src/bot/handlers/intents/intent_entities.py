from aiogram.types import Message
from src.ai.router import extract_entities, extract_inbox, extract_add_tasks
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
    
    from sqlalchemy import func
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    for p in extraction.projects:
        existing = db.query(Project).filter(Project.user_id == user.id, func.lower(Project.title) == p.title.lower()).first()
        if existing:
            await message.answer(f"⚠️ Project already exists: <b>{existing.title}</b>", parse_mode="HTML")
            continue
            
        proj = Project(user_id=user.id, title=p.title, status="active", target_value=p.target_value)
        db.add(proj)
        db.flush()
        
        # Log action for SMART UNDO
        from src.db.models import ActionLog
        import json
        alog = ActionLog(user_id=user.id, tool_name="create_project", previous_state_json={}, new_state_json={"project_id": proj.id})
        db.add(alog)
        
        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg, parse_mode="HTML")
        
    for h in extraction.habits:
        existing = db.query(Habit).filter(Habit.user_id == user.id, func.lower(Habit.title) == h.title.lower()).first()
        if existing:
            await message.answer(f"⚠️ Habit already exists: <b>{existing.title}</b>", parse_mode="HTML")
            continue

        unit = getattr(h, "unit", "times")
        habit = Habit(user_id=user.id, title=h.title, target_value=h.target_value, unit=unit, type="counter")
        db.add(habit)
        db.flush()
        
        # Log action for SMART UNDO
        from src.db.models import ActionLog
        import json
        alog = ActionLog(user_id=user.id, tool_name="create_habit", previous_state_json={}, new_state_json={"habit_id": habit.id})
        db.add(alog)
        
        await message.answer(f"✅ Habit created: <b>{habit.title}</b>", parse_mode="HTML")
        
    db.commit()


async def _handle_add_inbox(message: Message, db, user, provider_name, api_key):
    from src.db.models import Inbox
    from src.bot.handlers.utils import log_tokens
    
    extraction, tokens = extract_inbox, extract_add_tasks(message.text, provider_name, api_key)
    
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




async def _handle_add_tasks(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Task
    
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_projects_text = "User has no active projects yet."
    else:
        active_projects_text = "User's active projects:\n" + "\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    extraction, tokens = extract_add_tasks(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not extraction.tasks:
        await message.answer("I could not verify the exact tasks to add.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    count = 0
    msg_lines = []
    
    for t in extraction.tasks:
        project_id = t.project_id
        if project_id is None and t.unmatched_project_name:
            # We skip creating standalone tasks if they explicitly meant a project but we missed it. 
            # Or we could prompt a keyboard. Let's just create it as standalone and notify.
            pass
            
        task = Task(
            user_id=user.id,
            project_id=project_id,
            title=t.title,
            status='pending'
        )
        db.add(task)
        count += 1
        
        proj_name = "(Standalone)"
        if project_id:
            proj = next((p for p in projects if p.id == project_id), None)
            if proj:
                proj_name = proj.title
            
        msg_lines.append(f"• {t.title} 📂 <i>{proj_name}</i>")
        
    db.commit()
    
    nl = '\n'
    await message.answer(f"✅ <b>Added {count} task(s):</b>\n{nl.join(msg_lines)}", parse_mode="HTML")
