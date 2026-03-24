import re

with open("src/bot/handlers/ai_router.py", "r") as f:
    text = f.read()

text = text.replace("extract_system_config, extract_entities, generate_chat", "extract_system_config, extract_entities, generate_chat, extract_log_habit")

old_block = 'elif intent == IntentType.LOG_WORK:'
new_block = '''elif intent == IntentType.LOG_HABIT:
            return await _handle_log_habit(message, db, user, provider_name, real_api_key)
        elif intent == IntentType.LOG_WORK:'''

text = text.replace(old_block, new_block)

new_func = """
async def _handle_log_habit(message: Message, db, user, provider_name, api_key):
    from src.db.models import Habit
    from datetime import datetime, timezone

    # 1. Fetch active habits formatting for AI prompt
    habits = db.query(Habit).filter(Habit.user_id == user.id, Habit.status == 'active').all()
    if not habits:
        active_habits_text = "User has no active habits yet."
    else:
        active_habits_text = "User's active habits:\\n" + "\\n".join([f"ID: {h.id}, Title: {h.title}" for h in habits])

    # 2. Call AI extraction
    extraction, tokens = extract_log_habit(message.text, provider_name, api_key, active_habits_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction:
        await message.answer("I could not verify the exact habit to log.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if extraction.habit_id is None:
        title = extraction.unmatched_habit_name or "New Habit"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Click to Create", callback_data=f"create_habit_{title[:32]}")
        ]])
        await message.answer(f"🧩 I couldn't find a matching habit. Do you want to create <b>{title}</b>?", parse_mode="HTML", reply_markup=keyboard)
        return
        
    habit = db.query(Habit).filter_by(id=extraction.habit_id, user_id=user.id).first()
    if not habit:
        await message.answer("Error: AI returned an invalid Habit ID.")
        return

    # Log it
    habit.completions += extraction.amount_completed
    habit.last_completed_at = datetime.now(timezone.utc)
    db.commit()

    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\\n💬 <i>{desc}</i>" if desc else ""
    
    # We could add an UNDO button here! User asked for it.
    # For undo, we would ideally track history, but for habits we can just allow them to undo the completion
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_habit_{habit.id}_{extraction.amount_completed}")
    ]])
    
    await message.answer(
        f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\n"
        f"🏃 Total: {habit.completions}{append_desc}",
        parse_mode="HTML",
        reply_markup=keyboard
    )
"""

text += new_func

with open("src/bot/handlers/ai_router.py", "w") as f:
    f.write(text)

