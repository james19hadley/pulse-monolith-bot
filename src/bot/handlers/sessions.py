import datetime
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.db.repo import SessionLocal
from src.db.models import User, Session, TimeLog
from src.bot.handlers.utils import get_or_create_user

router = Router()

@router.message(Command("start_session"))
@router.message(F.text == "🟢 Start Session")
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
        
    await message.answer("🍅 Focus session started! Get working!")

@router.message(Command("end_session"))
@router.message(F.text == "🛑 End Session")
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
            
            # Log time
            log = TimeLog(
                user_id=user.id,
                session_id=session.id,
                duration_minutes=actual_duration_minutes,
                project_id=None,
                description="Completed Focus Session"
            )
            db.add(log)
            
            await message.answer(f"🍅 Focus session ended! You worked for {actual_duration_minutes} minutes.")
            
        user.active_session_id = None
        db.commit()

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


@router.message(F.text == "🌙 End Day")
@router.message(Command("end_day"))
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
                
                log = TimeLog(
                    user_id=user.id,
                    session_id=session.id,
                    duration_minutes=actual_duration_minutes,
                    project_id=None,
                    description="Completed Focus Session (End of Day)"
                )
                db.add(log)
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


@router.message(F.text == "🌙 End Day")
@router.message(Command("end_day"))
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
                
                log = TimeLog(
                    user_id=user.id,
                    session_id=session.id,
                    duration_minutes=actual_duration_minutes,
                    project_id=None,
                    description="Completed Focus Session (End of Day)"
                )
                db.add(log)
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
