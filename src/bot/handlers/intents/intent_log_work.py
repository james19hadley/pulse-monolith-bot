from aiogram.types import Message
from src.db.models import TokenUsage, Project, TimeLog, Habit, Session
from src.bot.texts import Prompts
from src.bot.handlers.utils import get_or_create_user
from src.ai.router import extract_log_work, extract_log_habit, extract_session_control
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
        session_id=user.active_session_id,
        project_id=project.id,
        duration_minutes=extraction.duration_minutes,
        progress_amount=extraction.progress_amount,
        progress_unit=extraction.progress_unit,
        description=extraction.description
    )
    db.add(log_entry)
    
    logged_progress = extraction.progress_amount
    if extraction.progress_amount is not None:
        if extraction.is_absolute_progress:
            delta = extraction.progress_amount - (project.current_value or 0.0)
            log_entry.progress_amount = delta
            project.current_value = extraction.progress_amount
            logged_progress = delta
        else:
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

    # Sprint 24: Check if there was a pending_split session
    if user.active_session_id:
        from src.db.models import Session
        session = db.query(Session).filter(Session.id == user.active_session_id).first()
        if session and session.status == "pending_split":
            session.status = "closed"
            user.active_session_id = None
            db.commit()
            msg_lines.append("\n✅ <i>Session closed. The rest of the time is written off to The Void.</i>")

    await message.answer(
        "\n".join(msg_lines),
        parse_mode="HTML",
        reply_markup=keyboard
    )


