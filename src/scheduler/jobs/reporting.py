"""
Daily accountability report generation.
@Architecture-Map: [JOB-REPORT]
"""
from datetime import datetime, timedelta, time
from src.db.repo import SessionLocal
from src.db.models import User, Project
from src.bot.handlers.utils import generate_daily_report_text
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from celery import shared_task

@shared_task(name="job_daily_accountability")
def daily_accountability_job():
    """
    Runs periodically (e.g. every hour) to build and post daily accountability reports
    for users whose day_cutoff_time has just passed.
    """
    import zoneinfo
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            try:
                user_tz = zoneinfo.ZoneInfo(user.timezone)
            except Exception:
                user_tz = zoneinfo.ZoneInfo("UTC")
            local_time = now_utc.astimezone(user_tz)

            already_done = False
            if user.last_manual_report_date and user.last_manual_report_date == local_time.date():
                already_done = True
                
            cutoff = getattr(user, 'day_cutoff_time', time(23, 0))
            
            current_mins = local_time.hour * 60 + local_time.minute
            cutoff_mins = cutoff.hour * 60 + cutoff.minute
            
            # How many minutes have passed since cutoff?
            mins_passed = current_mins - cutoff_mins
            if mins_passed < 0:
                mins_passed += 24 * 60
                
            # If we are within the first 15 minutes after the cutoff
            # (Matches Celery */15 crontab exactly once per day)
            if 0 <= mins_passed < 15:
                
                # 1. Send Auto-Report if they haven't manually requested one today
                if not already_done:
                    target_chat_id = user.target_channel_id or user.telegram_id
                    
                    try:
                        report_text = generate_daily_report_text(db, user, is_auto_cron=True)
                    except Exception as e:
                        print(f"Failed to build auto-report for {user.telegram_id}: {e}")
                        continue
                    if bot:
                        try:
                            run_async(bot.send_message(
                                chat_id=target_chat_id,
                                text=report_text,
                                parse_mode="HTML"
                            ))
                            # Mark as done so we don't spam them
                            user.last_manual_report_date = local_time.date()
                            db.commit()
                        except Exception as e:
                            print(f"Failed to send accountability report to {target_chat_id}: {e}")

                # 2. End of Day Reset: Explicitly after cutoff (runs regardless of already_done!)
                # Note: Because this runs exactly once in the 0-15 min window, we reset stats.
                # If the job runs multiple times in the 15 mins, stats will just be reset to 0 again.
                try:
                    projects = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None, Project.status == "active").all()
                    
                    is_sunday = local_time.weekday() == 6 # 0=Mon, 6=Sun
                    
                    # Check if tomorrow is the 1st of the month
                    next_day = local_time.date() + timedelta(days=1)
                    is_end_of_month = next_day.day == 1
                    
                    for p in projects:
                        target_period = getattr(p, 'target_period', 'daily')
                        should_reset = False
                        
                        if target_period == 'daily':
                            should_reset = True
                        elif target_period == 'weekly' and is_sunday:
                            should_reset = True
                        elif target_period == 'monthly' and is_end_of_month:
                            should_reset = True
                            
                        if should_reset:
                            if (p.daily_progress or 0) < p.daily_target_value:
                                p.current_streak = 0
                            p.daily_progress = 0
                            
                    db.commit()
                except Exception as e:
                    print(f"Failed to reset daily stats for user {user.telegram_id}: {e}")
                    db.rollback()
