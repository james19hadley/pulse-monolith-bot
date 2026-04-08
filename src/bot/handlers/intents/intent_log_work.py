from aiogram.types import Message
from src.db.models import TokenUsage, Project, TimeLog, Session
from src.bot.texts import Prompts
from src.bot.handlers.utils import log_tokens
from src.bot.handlers.utils import get_or_create_user
from src.ai.router import extract_log_work, extract_session_control
from datetime import datetime, timezone

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

    if extraction.project_id is None or extraction.project_id == 0:
        # Fallback to Project 0: Operations for pure time logging
        from src.bot.handlers.utils import get_or_create_project_zero
        project = get_or_create_project_zero(db, user.id)
        extraction.project_id = project.id
        
    project = db.query(Project).filter_by(id=extraction.project_id, user_id=user.id).first()
    if not project:
        await message.answer("Error: AI returned an invalid Project ID.")
        return

    # Log it
    log_entry = TimeLog(
        user_id=user.id,
        session_id=user.active_session_id,
        project_id=project.id,
        duration_minutes=extraction.duration_minutes,
        progress_amount=extraction.progress_amount,
        progress_unit=extraction.progress_unit,
        description=extraction.description
    )
    db.add(log_entry)
    
    logged_progress = extraction.progress_amount
    amount_to_add = 0
    is_time_based = not project.unit or project.unit in ['minutes', 'hours']

    # 1. Determine what we logged based on what AI extracted
    if extraction.progress_amount is not None:
        if extraction.is_absolute_progress:
            delta = extraction.progress_amount - (project.current_value or 0.0)
            log_entry.progress_amount = delta
            project.current_value = extraction.progress_amount
            logged_progress = delta
            amount_to_add = delta
        else:
            project.current_value = max(0.0, (project.current_value or 0.0) + extraction.progress_amount)
            amount_to_add = extraction.progress_amount
            
        if not project.unit and extraction.progress_unit:
            project.unit = extraction.progress_unit
    else:
        # If no explicit progress, fallback to time
        if extraction.duration_minutes != 0:
            amount_to_add = extraction.duration_minutes
            if is_time_based:
                project.current_value = max(0.0, (project.current_value or 0.0) + extraction.duration_minutes)
                
    # 2. AUTO-FILL logic: If the user just said "did my habit" (0 mins, 0 progress extracted)
    if amount_to_add == 0 and project.daily_target_value is not None:
        remains = project.daily_target_value - (project.daily_progress or 0)
        if remains > 0:
            amount_to_add = remains
            if is_time_based:
                log_entry.duration_minutes = amount_to_add
                project.current_value = max(0.0, (project.current_value or 0.0) + amount_to_add)
            else:
                log_entry.progress_amount = amount_to_add
                project.current_value = max(0.0, (project.current_value or 0.0) + amount_to_add)

    # 3. Update Daily target if applicable
    daily_msg = ""
    if project.daily_target_value is not None:
            old_daily = project.daily_progress or 0
            new_daily = max(0, old_daily + amount_to_add)
            project.daily_progress = new_daily
            
            if old_daily < project.daily_target_value and new_daily >= project.daily_target_value:
                project.total_completions = (project.total_completions or 0) + 1
                project.current_streak = (project.current_streak or 0) + 1
                daily_msg = f"🔥 Target Completed! ({new_daily:g} / {project.daily_target_value:g} {project.unit or 'minutes'}) 🏆 Streak: {project.current_streak}"
            else:
                daily_msg = f"🔥 Daily target progress: {new_daily:g} / {project.daily_target_value:g} {project.unit or 'minutes'}"

    db.commit()
    db.refresh(log_entry)


    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\n💬 <i>{desc}</i>" if desc else ""
    
    from src.bot.keyboards import get_main_menu
    keyboard = get_main_menu()
    
    msg_lines = []
    
    if daily_msg:
        msg_lines.append(daily_msg)
    
    if extraction.duration_minutes > 0:
        hours = extraction.duration_minutes / 60
        msg_lines.append(f"✅ Logged <b>{hours:g}h</b> to <b>{project.title}</b>!")
        # Optional: total time
    else:
        msg_lines.append(f"✅ Updated <b>{project.title}</b>!")

    if logged_progress is not None:
        unit_str = f" {extraction.progress_unit}" if extraction.progress_unit else " units"
        if extraction.is_absolute_progress:
            msg_lines.append(f"📈 Progress set to: {extraction.progress_amount}{unit_str} (Delta: {logged_progress:g})")
        else:
            msg_lines.append(f"📈 Progress: +{logged_progress:g}{unit_str}")
        
    
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

    # ADD ACTION LOG FOR UNDO
    from src.db.models import ActionLog
    action = ActionLog(
        user_id=user.id,
        tool_name="log_work",
        previous_state_json={"amount": amount_to_add, "progress_amount": logged_progress},
        new_state_json={"log_id": log_entry.id, "project_id": project.id}
    )
    db.add(action)
    db.commit()

    # Sprint 24: Check if there was a pending_split session
    if user.active_session_id:
        from src.db.models import Session
        session = db.query(Session).filter(Session.id == user.active_session_id).first()
        if session and session.status == "pending_split":
            session.status = "closed"
            user.active_session_id = None
            db.commit()
            msg_lines.append("\n✅ <i>Session closed. The rest of the time is written off to Project 0.</i>")

    await message.answer(
        "\n".join(msg_lines),
        parse_mode="HTML",
        reply_markup=keyboard
    )


