import re

with open('src/bot/handlers/ai_router.py', 'r') as f:
    text = f.read()

# Make sure extract_log_work is imported
if 'extract_log_work' not in text:
    text = text.replace('extract_log_habit', 'extract_log_habit, extract_log_work')

# Replace the specific hardcoded LOG_WORK processing
old_log_work = """        elif intent == IntentType.LOG_WORK:
            await message.answer("Please use <code>/log &lt;minutes&gt; [description]</code> to log time.", parse_mode="HTML")"""

new_log_work = """        elif intent == IntentType.LOG_WORK:
            return await _handle_log_work(message, db, user, provider_name, real_api_key)"""

text = text.replace(old_log_work, new_log_work)

# Add _handle_log_work function
new_func = """
async def _handle_log_work(message: Message, db: Session, user: User, provider_name: str, api_key: str):
    from src.db.models import Project
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_proj_text = "User has no active projects yet."
    else:
        active_proj_text = "User's active projects:\\n" + "\\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    extraction, tokens = extract_log_work(message.text, provider_name, api_key, active_proj_text)
    
    if tokens:
        log_tokens(db, user.telegram_id, tokens)
        
    if not extraction:
        await message.answer("I could not verify the exact project or time to log.")
        return
        
    if extraction.project_id is None:
        title = extraction.unmatched_project_name or "New Project"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➕ Create new project", callback_data=f"create_project:{title[:15]}")
        ]])
        await message.answer(f"Let's put this time into a project. I couldn't find a matching active project.", reply_markup=keyboard)
        return
        
    project = db.query(Project).filter(Project.id == extraction.project_id).first()
    if not project:
        await message.answer("Project not found.")
        return
        
    from src.bot.handlers.core import process_log_entry
    await process_log_entry(message, db, user, extraction.duration_minutes, extraction.description, project)
"""

if "_handle_log_work(" not in text:
    text += new_func

with open('src/bot/handlers/ai_router.py', 'w') as f:
    f.write(text)
