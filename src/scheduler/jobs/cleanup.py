"""
Automatic closing of stale sessions.
@Architecture-Map: [JOB-CLEANUP]
"""
from datetime import datetime, timedelta
from src.db.repo import SessionLocal
from src.db.models import User, Session as AppSession, TimeLog
from src.bot.views import stale_session_closed_message
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from celery import shared_task

@shared_task(name="job_stale_session_killer")
def stale_session_killer():
    """
    Runs periodically (e.g. every hour). Ends sessions that have been open for over 16 hours.
    """
    with SessionLocal() as db:
        active_sessions = db.query(AppSession).filter(AppSession.status.in_(["active", "rest", "pending_split"])).all()
        now = datetime.utcnow()
        for session in active_sessions:
            duration_hours = (now - session.start_time).total_seconds() / 3600
            if duration_hours > 16:
                last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
                if last_log:
                    close_time = last_log.created_at + timedelta(minutes=last_log.duration_minutes or 0)
                else:
                    close_time = session.start_time + timedelta(minutes=1)
                
                session.status = "closed"
                session.end_time = close_time
                
                user = db.query(User).filter(User.id == session.user_id).first()
                if user and user.active_session_id == session.id:
                    user.active_session_id = None
                    
                db.commit()
                if user and bot:
                    try:
                        run_async(bot.send_message(
                            chat_id=user.telegram_id,
                            text=stale_session_closed_message()
                        ))
                    except Exception as e:
                        print(f"Failed to send stale session notice to {user.telegram_id}: {e}")
