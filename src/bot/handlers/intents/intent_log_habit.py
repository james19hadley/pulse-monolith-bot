from aiogram.types import Message
from src.db.models import TokenUsage, Project, TimeLog, Habit, Session
from src.bot.texts import Prompts
from src.bot.handlers.utils import log_tokens
from src.bot.handlers.utils import get_or_create_user
from src.ai.router import extract_log_work, extract_log_habit, extract_session_control
from datetime import datetime, timezone

async def _handle_log_habit(message: Message, db, user, provider_name, api_key):
    from src.db.models import Habit
    from datetime import datetime, timezone

    # 1. Fetch active habits formatting for AI prompt
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    if not habits:
        active_habits_text = "User has no active habits yet."
    else:
        active_habits_text = "User's active habits:\n" + "\n".join([f"ID: {h.id}, Title: {h.title}" for h in habits])

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
    if extraction.amount_completed == 1 and habit.target_value > 1 and "done" not in message.text.lower() and "выполнил" not in message.text.lower():
        habit.current_value += extraction.amount_completed
    else:
        habit.current_value = habit.target_value if extraction.amount_completed == 1 else habit.current_value + extraction.amount_completed
        from datetime import timedelta
    
    # Calculate streak logic if this log finishes the daily target
    streak_msg = ""
    # We only increment streaks/completions if the habit hits the target threshold
    if habit.current_value >= habit.target_value:
        habit.total_completions += 1
        
        # Streak Calculation
        today = datetime.now(timezone.utc).date()
        if not habit.last_completed_at:
            # First time completely finishing
            habit.current_streak = 1
        else:
            last_date = habit.last_completed_at.date()
            if last_date == today:
                pass # Already completed today
            elif last_date == today - timedelta(days=1):
                # Consecutive day
                habit.current_streak += 1
            else:
                # Streak broken
                habit.current_streak = 1
                
        if habit.current_streak > 1:
            streak_msg = f"\n🔥 <b>Current Streak:</b> {habit.current_streak} days"
    habit.last_completed_at = datetime.now(timezone.utc)
    db.commit()

    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\n💬 <i>{desc}</i>" if desc else ""
    
    # We could add an UNDO button here! User asked for it.
    # For undo, we would ideally track history, but for habits we can just allow them to undo the completion
    
    await message.answer(
        f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\n" \
        f"🏃 Progress: {habit.current_value}/{habit.target_value}{streak_msg}{append_desc}",
        parse_mode="HTML"
    )


