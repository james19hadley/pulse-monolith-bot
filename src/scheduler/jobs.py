import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from src.db.repo import SessionLocal
from src.db.models import User, Session, TimeLog
from aiogram import Bot

# In-memory storage for last ping message ids to delete them later
last_ping_message_ids = {}

async def catalyst_heartbeat(bot: Bot):
    """
    Runs periodically. Checks for active sessions that have been idle 
    (no time logs) for over 1 hour. Sends a soft ping.
    """
    with SessionLocal() as db:
        active_sessions = db.query(Session).filter(Session.status == "active").all()
        
        for session in active_sessions:
            # Check last timelog for this session
            last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
            
            idle_since = last_log.created_at if last_log else session.start_time
            now = datetime.utcnow()
            
            # If idle for more than 60 minutes
            if now - idle_since > timedelta(minutes=60):
                user = db.query(User).filter(User.id == session.user_id).first()
                if not user:
                    continue
                    
                telegram_id = user.telegram_id
                
                # Try to delete previous ping to avoid wall of shame
                if telegram_id in last_ping_message_ids:
                    try:
                        await bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id])
                    except Exception:
                        pass # Message might already be deleted or not found
                
                # Send new ping
                hours_idle = int((now - idle_since).total_seconds() // 3600)
                try:
                    msg = await bot.send_message(
                        chat_id=telegram_id, 
                        text=f"The Void expands. You have not logged focus for {hours_idle} hour(s)."
                    )
                    last_ping_message_ids[telegram_id] = msg.message_id
                except Exception as e:
                    print(f"Failed to send ping to {telegram_id}: {e}")
