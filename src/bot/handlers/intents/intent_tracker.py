from aiogram.types import Message
from src.ai.router import extract_log_work, extract_log_habit
from src.bot.handlers.utils import log_tokens
async def _handle_log_work(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, TimeLog
    from datetime import datetime, timezone

    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_projects_text = "User has no active projects yet."
    else:
        active_projects_text = "User's active projects:\n" + "\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    # 2. Call AI extraction
    extraction, tokens = extract_log_work(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction:
        await message.answer("I could not verify the exact work/project to log.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if extraction.project_id is None:
        title = extraction.unmatched_project_name or "New Project"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Click to Create", callback_data=f"create_project_{title[:32]}")
        ]])
        await message.answer(f"🧩 I couldn't find a matching project. Do you want to create <b>{title}</b> first?", parse_mode="HTML", reply_markup=keyboard)
        return
        
    project = db.query(Project).filter_by(id=extraction.project_id, user_id=user.id).first()
    if not project:
        await message.answer("Error: AI returned an invalid Project ID.")
        return

    # Log it
    log_entry = TimeLog(
        user_id=user.id,
        project_id=project.id,
        duration_minutes=extraction.duration_minutes,
        progress_amount=extraction.progress_amount,
        progress_unit=extraction.progress_unit,
        description=extraction.description
    )
    db.add(log_entry)
    if extraction.progress_amount is not None:
        project.current_value = (project.current_value or 0.0) + extraction.progress_amount
        if not project.unit and extraction.progress_unit:
            project.unit = extraction.progress_unit
    else:
        project.current_value = (project.current_value or 0.0) + extraction.duration_minutes

            
    db.commit()
    db.refresh(log_entry)

    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\n💬 <i>{desc}</i>" if desc else ""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_work_{log_entry.id}")
    ]])
    
    msg_lines = []
    
    if extraction.duration_minutes > 0:
        hours = extraction.duration_minutes / 60
        msg_lines.append(f"✅ Logged <b>{hours:g}h</b> to <b>{project.title}</b>!")
        # Optional: total time
    else:
        msg_lines.append(f"✅ Updated <b>{project.title}</b>!")

    if extraction.progress_amount is not None:
        unit_str = f" {extraction.progress_unit}" if extraction.progress_unit else " units"
        msg_lines.append(f"📈 Progress: +{extraction.progress_amount}{unit_str}")
        
    
    if project.unit == 'minutes' or not project.unit:
        cur_h = (project.current_value or 0) / 60
        target_h = (project.target_value or 0) / 60
        if project.target_value:
            from src.bot.views import build_progress_bar
            bar = build_progress_bar(project.current_value or 0, project.target_value)
            msg_lines.append(f"📉 Total Progress: {cur_h:g} / {target_h:g} hours\n{bar}")
        else:
            msg_lines.append(f"📉 Total Progress: {cur_h:g} hours")
    else:
        if project.target_value:
            from src.bot.views import build_progress_bar
            bar = build_progress_bar(project.current_value or 0, project.target_value)
            msg_lines.append(f"📉 Total Progress: {project.current_value or 0:g} / {project.target_value:g} {project.unit}\n{bar}")
        else:
            msg_lines.append(f"📉 Total Progress: {project.current_value or 0:g} {project.unit}")
    
    if append_desc:
        msg_lines.append(append_desc)

    await message.answer(
        "\n".join(msg_lines),
        parse_mode="HTML",
        reply_markup=keyboard
    )


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
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_habit_{habit.id}_{extraction.amount_completed}")
    ]])
    
    await message.answer(
        f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\n" \
        f"🏃 Progress: {habit.current_value}/{habit.target_value}{streak_msg}{append_desc}",
        parse_mode="HTML",
        reply_markup=keyboard
    )



