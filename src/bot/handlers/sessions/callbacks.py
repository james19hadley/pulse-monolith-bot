"""
Callback handlers for session project assignment and nudges.
@Architecture-Map: [HND-SESS-CB]
"""
import datetime
from aiogram import F
from aiogram.types import CallbackQuery
from src.db.repo import SessionLocal
from src.db.models import User, Session, TimeLog, Project
from src.bot.handlers.utils import get_or_create_user
from src.bot.keyboards import get_main_menu
from aiogram import Router

router = Router()

@router.callback_query(F.data.startswith("ses_proj_"))
async def cq_assign_session_project(callback_query: CallbackQuery):
    action = callback_query.data.replace("ses_proj_", "")
    
    if action == "skip":
         await callback_query.message.edit_text("⏱ Таймер запущен. Работаем в фоне.")
         return
         
    try:
         proj_id = int(action)
    except ValueError:
         await callback_query.answer("Invalid project ID")
         return
         
    with SessionLocal() as db:
         user = get_or_create_user(db, callback_query.from_user.id)
         if not user.active_session_id:
              await callback_query.message.edit_text("Сессия уже закрыта или не существует.")
              return
              
         session = db.query(Session).filter(Session.id == user.active_session_id).first()
         if session:
              session.project_id = proj_id
              proj = db.query(Project).filter(Project.id == proj_id).first()
              proj_title = proj.title if proj else f"Project {proj_id}"
              db.commit()
              await callback_query.message.edit_text(f"⏱ Таймер запущен. Цель: <b>{proj_title}</b>", parse_mode="HTML")
         else:
              await callback_query.message.edit_text("Сессия не найдена.")

@router.callback_query(F.data == "nudge_working")
async def handle_nudge_working_callback(callback_query: CallbackQuery):
    """
    User clicked 'Retroactive End'.
    End the session, but rewind the end_time by 1 hour (cutting off the dead time).
    """
    await callback_query.answer("Rewinding...")
    
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()
        if not user or not user.active_session_id: return
        
        session = db.query(Session).filter(Session.id == user.active_session_id).first()
        if session:
            end_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            if end_time < session.start_time:
                end_time = session.start_time
                
            session.end_time = end_time
            actual_duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
            session.status = "closed"
            
            log_project_id = None
            if session.project_id:
                project = db.query(Project).filter(Project.id == session.project_id).first()
                if project:
                    log_project_id = project.id
            
            if not log_project_id:
                from src.bot.handlers.utils import get_or_create_project_zero
                p_zero = get_or_create_project_zero(db, user.id)
                log_project_id = p_zero.id

            log = TimeLog(
                user_id=user.id,
                session_id=session.id,
                duration_minutes=actual_duration_minutes,
                project_id=log_project_id,
                description="Completed Focus Session (Retroactive)"
            )
            db.add(log)
            
            project = db.query(Project).filter(Project.id == log_project_id).first()
            if project and (project.unit == "minutes" or project.unit is None):
                project.current_value = (project.current_value or 0) + actual_duration_minutes
                if project.daily_target_value is not None:
                    project.daily_progress = (project.daily_progress or 0) + actual_duration_minutes
                
            user.active_session_id = None
            db.commit()

            from src.db.models import ActionLog
            action = ActionLog(
                user_id=user.id,
                tool_name="log_work",
                previous_state_json={"amount": actual_duration_minutes, "progress_amount": None},
                new_state_json={"log_id": log.id, "project_id": log_project_id}
            )
            db.add(action)
            db.commit()

            await callback_query.message.answer(f"🍅 Focus session ended retroactively! You worked for {actual_duration_minutes} minutes.", reply_markup=get_main_menu(False))

@router.callback_query(F.data == "nudge_finish")
async def handle_nudge_finish_callback(callback_query: CallbackQuery):
    """
    User clicked 'Finish session' on a nudge message. 
    Redirect to standard session end flow.
    """
    await callback_query.answer()
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
        
    from .commands import cmd_end_session
    await cmd_end_session(callback_query.message)
