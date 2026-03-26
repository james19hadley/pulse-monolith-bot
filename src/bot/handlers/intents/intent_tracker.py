import json
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from src.db.models import User, Session as AppSession, TimeLog, Project, Habit, Inbox
from src.ai.providers import GoogleProvider
from src.bot.views import (
    unknown_command_message, error_message, project_list_message,
    session_opened_message, undo_success_message, undo_fail_message,
    nothing_to_undo_message
)

async def _handle_log_work(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.LOG_WORK - tracks time and progress against a Project"""
    provider = GoogleProvider(api_key=api_key)
    
    # 1. Fetch user's projects to provide context to LLM
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
    if not projects:
        await message.answer("You have no active projects to log work against. Create one first!")
        return

    projects_context = [{"id": p.id, "title": p.title, "unit": p.unit} for p in projects]
    prompt = f"Extract work log details from: '{message.text}'. Available projects: {json.dumps(projects_context, ensure_ascii=False)}"
    
    response, tokens = provider.generate_structured_response(prompt, "LogWorkParams")
    from src.bot.handlers.utils import log_tokens
    log_tokens(db, user.telegram_id, tokens)
    
    if not response or not getattr(response, "project_id", None) or not getattr(response, "duration_minutes", None):
        await message.answer(unknown_command_message())
        return

    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == response.project_id, Project.user_id == user.id).first()
    if not project:
        await message.answer("❌ Invalid project ID extracted. Please try again.")
        return

    # Handle active session logic
    session = None
    if user.active_session_id:
        session = db.query(AppSession).filter(AppSession.id == user.active_session_id).first()
    
    if not session:
        session = AppSession(user_id=user.id, status="active")
        db.add(session)
        db.commit()
        db.refresh(session)
        user.active_session_id = session.id
        await message.answer(session_opened_message())
    
    # Update project progress conditionally
    progress_made = response.progress_amount or 0
    if project.unit == "minutes":
        project.current_value += response.duration_minutes
    else:
        project.current_value += progress_made
        
    db.add(project)
    
    log = TimeLog(
        user_id=user.id,
        session_id=session.id,
        project_id=project.id,
        duration_minutes=response.duration_minutes,
        progress_amount=progress_made
    )
    db.add(log)
    user.last_action_type = "time_log"
    user.last_action_id = log.id
    db.commit()
    
    unit_str = f" {project.unit}" if project.unit and project.unit != "minutes" else ""
    prog_str = f" (+{progress_made}{unit_str})" if progress_made > 0 else ""
    progress_bar = ""
    if project.unit != "minutes" and project.target_value:
        from src.bot.views import build_progress_bar
        progress_bar = "\n" + build_progress_bar(project.current_value, project.target_value)
        
    await message.answer(
        f"⏱ Logged <b>{response.duration_minutes}m</b> to <b>{project.title}</b>{prog_str}.{progress_bar}\n"
        f"<i>\"{getattr(response, 'log_summary', 'Work logged')}\"</i>"
    )

async def _handle_log_habit(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.LOG_HABIT"""
    provider = GoogleProvider(api_key=api_key)
    
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    if not habits:
        await message.answer("You have no configured habits.")
        return

    habits_context = [{"id": h.id, "title": h.title, "type": h.type} for h in habits]
    prompt = f"Extract habit log details from: '{message.text}'. Available habits: {json.dumps(habits_context, ensure_ascii=False)}"
    
    response, tokens = provider.generate_structured_response(prompt, "LogHabitParams")
    from src.bot.handlers.utils import log_tokens
    log_tokens(db, user.telegram_id, tokens)
    
    if not response or not getattr(response, "habit_id", None):
        await message.answer(unknown_command_message())
        return

    habit = db.query(Habit).filter(Habit.id == response.habit_id, Habit.user_id == user.id).first()
    if not habit:
        await message.answer("❌ Invalid habit ID.")
        return

    val = getattr(response, "value", 1) or 1
    habit.current_value += val
    
    # Auto-complete streak logic if target reached
    completion_msg = ""
    if habit.current_value >= habit.target_value:
        habit.total_completions += 1
        habit.current_streak += 1
        # reset for next period
        habit.current_value = 0
        from src.bot.views import habit_updated_message
        completion_msg = f"\n🎉 Target reached! Streak: <b>{habit.current_streak}</b>"
    
    db.commit()
    await message.answer(
        f"📈 Logged <b>+{val}</b> to habit <b>{habit.title}</b>.\n"
        f"Progress: {habit.current_value}/{habit.target_value}{completion_msg}"
    )
