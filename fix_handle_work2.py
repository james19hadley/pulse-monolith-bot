import re

with open('src/bot/handlers/ai_router.py', 'r') as f:
    text = f.read()

old_func_part1 = """    from src.bot.handlers.core import process_log_entry
    await process_log_entry(message, db, user, extraction.duration_minutes, extraction.description, project)"""

new_func_part1 = """    from src.db.models import TimeLog
    import json
    
    # Store old state for undo
    old_state = {"project_id": project.id, "total_minutes_spent": project.total_minutes_spent}
    
    project.total_minutes_spent += extraction.duration_minutes
    log = TimeLog(
        user_id=user.id,
        session_id=user.active_session_id,
        project_id=project.id,
        duration_minutes=extraction.duration_minutes,
        description=extraction.description or "AI logged work"
    )
    db.add(log)
    db.flush() # flush to get log.id
    
    from src.bot.handlers.utils import log_action
    new_state = {"project_id": project.id, "total_minutes_spent": project.total_minutes_spent}
    log_action(db, user.id, "LOG_WORK", old_state, new_state)
    db.commit()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Undo", callback_data=f"undo:work:{log.id}")
    ]])
        
    await message.answer(f"✅ Logged <b>{extraction.duration_minutes}m</b> to <b>{project.title}</b>.\\n<i>{extraction.description or ''}</i>", reply_markup=keyboard, parse_mode="HTML")"""

text = text.replace(old_func_part1, new_func_part1)

with open('src/bot/handlers/ai_router.py', 'w') as f:
    f.write(text)
