import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from src.db.repo import SessionLocal
from src.db.models import User, Session, TimeLog
from aiogram import Bot

from src.bot.views import catalyst_ping_message, stale_session_closed_message

# In-memory storage for last ping message ids and timestamps
last_ping_message_ids = {}
last_ping_timestamps = {}

async def catalyst_heartbeat(bot: Bot):
    """
    Runs periodically. Checks for active sessions that have been idle
    (no time logs) for over the user's threshold. Sends a soft ping.
    """
    with SessionLocal() as db:
        active_sessions = db.query(Session).filter(Session.status == "active").all()
        for session in active_sessions:
            last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
            idle_since = last_log.created_at if last_log else session.start_time
            now = datetime.utcnow()
            
            user = db.query(User).filter(User.id == session.user_id).first()
            if not user:
                continue
                
            threshold_minutes = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes is not None else 60
            interval_minutes = user.catalyst_interval_minutes if user.catalyst_interval_minutes is not None else 20
            telegram_id = user.telegram_id
            
            if threshold_minutes <= 0:
                continue # User fully disabled catalyst heartbeat
                
            if now - idle_since > timedelta(minutes=threshold_minutes):
                last_ping_time = last_ping_timestamps.get(telegram_id)
                already_pinged = (last_ping_time is not None and last_ping_time >= idle_since)
                
                # Logic for interval repeat
                if interval_minutes <= 0 and already_pinged:
                    continue # Do not repeat ping
                if interval_minutes > 0 and already_pinged:
                    if (now - last_ping_time) < timedelta(minutes=interval_minutes):
                        continue # Not enough time passed for the next ping
                
                # Delete old ping message if exists
                if telegram_id in last_ping_message_ids:
                    try:
                        await bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id])
                    except Exception:
                        pass
                
                hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                try:
                    msg = await bot.send_message(
                        chat_id=telegram_id, 
                        text=catalyst_ping_message(hours_idle)
                    )
                    last_ping_message_ids[telegram_id] = msg.message_id
                    last_ping_timestamps[telegram_id] = now
                except Exception as e:
                    print(f"Failed to send ping to {telegram_id}: {e}")

async def stale_session_killer(bot: Bot):
    """
    Runs periodically (e.g. every hour). Ends sessions that have been open for over 16 hours.
    """
    with SessionLocal() as db:
        active_sessions = db.query(Session).filter(Session.status == "active").all()
        now = datetime.utcnow()
        for session in active_sessions:
            duration_hours = (now - session.start_time).total_seconds() / 3600
            if duration_hours > 16:
                last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
                if last_log:
                    close_time = last_log.created_at + timedelta(minutes=last_log.duration_minutes or 0)
                else:
                    close_time = session.start_time + timedelta(minutes=1)
                
                session.status = "ended"
                session.end_time = close_time
                db.commit()
                
                user = db.query(User).filter(User.id == session.user_id).first()
                if user:
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=stale_session_closed_message()
                        )
                    except Exception as e:
                        print(f"Failed to send stale session notice to {user.telegram_id}: {e}")
