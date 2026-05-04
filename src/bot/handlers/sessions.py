"""
Telegram handlers for starting, pausing, and ending work sessions.

@Architecture-Map: [HND-SESSIONS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.db.repo import SessionLocal
from src.db.models import User, Session, TimeLog, Project
from src.bot.handlers.utils import get_or_create_user
from src.bot.keyboards import get_main_menu

from src.bot.texts import Buttons

router = Router()

@router.message(Command("start_session"))
@router.message(F.text == Buttons.START_SESSION)
async def cmd_start_session(message: Message, command: CommandObject = None):
    """Start a new focus session."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        if user.active_session_id:
            await message.answer("You already have an active session! Use /end_session to stop it.")
            return

        session = Session(
            user_id=user.id,
            start_time=datetime.datetime.utcnow(),
            status="active"
        )
        db.add(session)
        db.flush()
        
        user.active_session_id = session.id
        db.commit()
    
        await message.answer("🟢 Сессия начата.", reply_markup=get_main_menu(True))
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from src.db.models import Project
        
        kb = []
        projects = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").order_by(Project.id.desc()).limit(3).all()
        for p in projects:
             kb.append([InlineKeyboardButton(text=p.title, callback_data=f"ses_proj_{p.id}")])
             
        kb.append([InlineKeyboardButton(text="Skip", callback_data="ses_proj_skip")])
        markup = InlineKeyboardMarkup(inline_keyboard=kb)
            
        await message.answer("⏱ Таймер запущен. Над чем работаем?", reply_markup=markup)

from aiogram import F
from aiogram.types import CallbackQuery

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
              
              from src.db.models import Project
              proj = db.query(Project).filter(Project.id == proj_id).first()
              proj_title = proj.title if proj else f"Project {proj_id}"
              
              db.commit()
              await callback_query.message.edit_text(f"⏱ Таймер запущен. Цель: <b>{proj_title}</b>", parse_mode="HTML")
         else:
              await callback_query.message.edit_text("Сессия не найдена.")

@router.message(Command("end_session"))
@router.message(F.text == Buttons.END_SESSION)
async def cmd_end_session(message: Message):
    """Stop the current focus session."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        if not user.active_session_id:
            await message.answer("You don't have an active session to end. Start one with /start_session.")
            return

        session = db.query(Session).filter(Session.id == user.active_session_id).first()
        if session:
            session.end_time = datetime.datetime.utcnow()
            actual_duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
            session.status = "closed"
            
            # Determine the correct project to log time to
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
                description="Completed Focus Session"
            )
            db.add(log)
            
            # Update project progress ONLY if it's a time-based project
            project = db.query(Project).filter(Project.id == log_project_id).first()
            if project and (project.unit == "minutes" or project.unit is None):
                project.current_value = (project.current_value or 0) + actual_duration_minutes
                if project.daily_target_value is not None:
                    project.daily_progress = (project.daily_progress or 0) + actual_duration_minutes
                
            user.active_session_id = None
            db.commit()
            db.refresh(log)

            from src.db.models import ActionLog
            action = ActionLog(
                user_id=user.id,
                tool_name="log_work",
                previous_state_json={"amount": actual_duration_minutes, "progress_amount": None},
                new_state_json={"log_id": log.id, "project_id": log_project_id}
            )
            db.add(action)
            db.commit()

            await message.answer(f"🍅 Focus session ended! You worked for {actual_duration_minutes} minutes.", reply_markup=get_main_menu(False))
            return

@router.message(Command("log"))
async def cmd_log(message: Message, command: CommandObject):
    """Log time manually. Usage: /log <minutes> [description]"""
    if not command.args:
        await message.answer("Usage: <code>/log &lt;minutes&gt; [description]</code>", parse_mode="HTML")
        return
        
    parts = command.args.split(maxsplit=1)
    
    try:
        minutes = int(parts[0])
    except ValueError:
        await message.answer("Error: minutes must be an integer.", parse_mode="HTML")
        return
        
    desc = parts[1] if len(parts) > 1 else "Manual log"
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        log = TimeLog(
            user_id=user.id,
            session_id=user.active_session_id if user.active_session_id else None,
            duration_minutes=minutes,
            description=desc
        )
        db.add(log)
        db.commit()
        
    await message.answer(f"Logged {minutes}m: {desc}", parse_mode="HTML")


@router.message(Command("end_day"))
@router.message(F.text.in_({Buttons.END_DAY, " " + Buttons.END_DAY}))
async def cmd_end_day(message: Message):
    """End the day, generate a report, and optionally send it to the accountability channel."""
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        # 1. Close active session if any
        if user.active_session_id:
            session = db.query(Session).filter(Session.id == user.active_session_id).first()
            if session:
                session.end_time = datetime.datetime.utcnow()
                actual_duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
                session.status = "closed"
                
                from src.bot.handlers.utils import get_or_create_project_zero
                p_zero = get_or_create_project_zero(db, user.id)

                log = TimeLog(
                    user_id=user.id,
                    session_id=session.id,
                    duration_minutes=actual_duration_minutes,
                    project_id=p_zero.id,
                    description="Completed Focus Session (End of Day)"
                )
                db.add(log)
                p_zero.current_value = (p_zero.current_value or 0) + actual_duration_minutes
                if p_zero.daily_target_value is not None:
                    p_zero.daily_progress = (p_zero.daily_progress or 0) + actual_duration_minutes
            user.active_session_id = None
            db.commit()
            await message.answer(f"🍅 Active session closed automatically ({actual_duration_minutes}m).")

        # 2. Generate Report
        import datetime
        user.last_manual_report_date = datetime.datetime.utcnow().date()
        db.commit()
        
        from src.bot.handlers.utils import generate_daily_report_text
        report_text = generate_daily_report_text(db, user)
        
        # 3. Deliver Report
        target_channel = getattr(user, 'target_channel_id', None)
        
        if target_channel and target_channel != "None":
            try:
                await message.bot.send_message(
                    chat_id=target_channel,
                    text=report_text,
                    parse_mode="HTML"
                )
                await message.answer(f"✅ Your End-of-Day report has been posted to your accountability channel!", parse_mode="HTML")
            except Exception as e:
                print(f"Failed to send to channel {target_channel}: {e}")
                await message.answer(f"""❌ Could not post to channel (ID: {target_channel}). Make sure I am an admin.

Here is your report anyway:

{report_text}""", parse_mode="HTML")
        else:
            await message.answer(f"""🌙 <b>End of Day</b>

{report_text}

<i>Tip: Bind a channel to post this automatically by forwarding a message from it!</i>""", parse_mode="HTML")


@router.callback_query(F.data == "nudge_working")
async def handle_nudge_working_callback(callback_query: CallbackQuery):
    """
    User clicked 'Retroactive End'.
    End the session, but rewind the end_time by 1 hour (cutting off the dead time).
    """
    await callback_query.answer("Rewinding...")
    
    # Clean the keyboard
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()
        if not user or not user.active_session_id: return
        
        session = db.query(Session).filter(Session.id == user.active_session_id).first()
        if session:
            # End the session 1 hour ago
            end_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            # Make sure end_time is not before start_time
            if end_time < session.start_time:
                end_time = session.start_time
                
            session.end_time = end_time
            actual_duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
            session.status = "closed"
            
            # Determine the correct project to log time to
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
            
            # Update project progress ONLY if it's a time-based project
            project = db.query(Project).filter(Project.id == log_project_id).first()
            if project and (project.unit == "minutes" or project.unit is None):
                project.current_value = (project.current_value or 0) + actual_duration_minutes
                if project.daily_target_value is not None:
                    project.daily_progress = (project.daily_progress or 0) + actual_duration_minutes
                
            user.active_session_id = None
            db.commit()
            db.refresh(log)

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
            return

@router.callback_query(F.data == "nudge_finish")
async def handle_nudge_finish_callback(callback_query: CallbackQuery):
    """
    User clicked 'Finish session' on a nudge message. 
    Redirect to standard session end flow.
    """
    await callback_query.answer()
    
    # Clean the keyboard
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
        
    await cmd_end_session(callback_query.message)
