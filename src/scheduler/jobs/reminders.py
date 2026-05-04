"""
Task reminder delivery.
@Architecture-Map: [JOB-REMIND]
"""
import html
from src.db.repo import SessionLocal
from src.db.models import Task, User
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from celery import shared_task

@shared_task(name="job_send_task_reminder")
def send_task_reminder_job(task_id: int):
    """
    Called by Celery (via ETA) exactly at the time the reminder should fire.
    """
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        # If the task was deleted, completed, or already sent, abort.
        if not task or task.status != 'pending' or task.is_reminder_sent:
            return
            
        user = db.query(User).filter(User.id == task.user_id).first()
        if not user:
            return
            
        try:
            target_chat_id = user.target_channel_id or user.telegram_id
            msg = f"⏰ <b>Напоминание:</b> {html.escape(task.title)}"
            if bot:
                run_async(bot.send_message(chat_id=target_chat_id, text=msg, parse_mode="HTML"))
            task.is_reminder_sent = True
            db.commit()
        except Exception as e:
            print(f"Failed to send task reminder to {user.telegram_id}: {e}")
