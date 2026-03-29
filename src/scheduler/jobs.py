import os
import asyncio
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from src.db.repo import SessionLocal
from src.db.models import User, Session as AppSession, TimeLog, Habit, Inbox, Project, Task, Task
from aiogram import Bot

from src.bot.views import catalyst_ping_message, stale_session_closed_message
from src.bot.handlers.utils import generate_daily_report_text
from src.ai.providers import GoogleProvider
from src.core.security import decrypt_key

from celery import shared_task
from src.scheduler.tasks import run_async

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    bot = None
else:
    bot = Bot(token=BOT_TOKEN)

# In-memory storage for last ping message ids and timestamps
last_ping_message_ids = {}
last_ping_timestamps = {}

@shared_task(name="job_catalyst_heartbeat")
def catalyst_heartbeat():
    """
    Runs periodically. Checks for active sessions that have been idle
    (no time logs) for over the user's threshold. Sends a soft ping.
    """
    with SessionLocal() as db:
        active_sessions = db.query(AppSession).filter(AppSession.status.in_(["active", "rest"])).all()
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
            
            # Sprint 24 Guardrails Processing
            is_ping_due = False
            ping_text = ""
            
            if session.status == "active":
                if threshold_minutes <= 0:
                    continue
                if now - idle_since > timedelta(minutes=threshold_minutes):
                    # Active session idling
                    hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                    is_ping_due = True
                    ping_text = f"⏳ Слышишь, ты уже в контексте сессии {hours_idle} часа(ов) без логов. Всё еще в потоке, или пора завершить сессию?"
            elif session.status == "rest":
                # Rest mode for > 30 minutes
                if session.rest_start_time and (now - session.rest_start_time > timedelta(minutes=30)):
                    mins_rested = int((now - session.rest_start_time).total_seconds() / 60)
                    is_ping_due = True
                    # Let's not annoy them every 5 mins. Use `last_ping_timestamps` to throttle.
                    ctx_text = f" Твой Save-State: «{session.save_state_context}»." if session.save_state_context else ""
                    ping_text = f"⏸️ Перерыв затянулся: меня не было {mins_rested} минут.{ctx_text} Возвращаемся или заканчиваем на сегодня?"

            if is_ping_due:
                last_ping_time = last_ping_timestamps.get(telegram_id)
                last_event_time = session.rest_start_time if session.status == 'rest' else idle_since
                if last_event_time is None: last_event_time = now
                
                already_pinged = (last_ping_time is not None and last_ping_time >= last_event_time)
                
                # Logic for interval repeat
                if interval_minutes <= 0 and already_pinged:
                    continue
                if interval_minutes > 0 and already_pinged:
                    if (now - last_ping_time) < timedelta(minutes=interval_minutes):
                        continue
                
                if telegram_id in last_ping_message_ids:
                    try:
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id]))
                    except Exception:
                        pass
                
                try:
                    if bot:
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=ping_text
                        ))
                        last_ping_message_ids[telegram_id] = msg.message_id
                        last_ping_timestamps[telegram_id] = now
                except Exception as e:
                    print(f"Failed to send ping to {telegram_id}: {e}")

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

@shared_task(name="job_daily_accountability")
def daily_accountability_job():
    """
    Runs periodically (e.g. every hour) to build and post daily accountability reports
    for users whose day_cutoff_time has just passed.
    """
    now = datetime.utcnow()
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            # We assume bot runs in UTC and user day_cutoff_time is also assumed to be matched against UTC for simplicity in this MVP.
            # In a real app we'd convert `now` to user.timezone and compare against user.day_cutoff_time.
            # Let's say we check if current hour/minute matches cutoff time
            # Check if auto-report was already pre-empted manually today
            already_done = False
            if user.last_manual_report_date and user.last_manual_report_date == now.date():
                already_done = True
                
            if now.hour == user.day_cutoff_time.hour and 0 <= now.minute < 60 and not already_done: # Runs once an hour roughly
                
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
                    except Exception as e:
                        print(f"Failed to send accountability report to {target_chat_id}: {e}")

@shared_task(name="job_evening_nudge")
def evening_nudge_job():
    """
    Runs periodically. Checks for habits that haven't been logged in over their nudge_threshold_days.
    Sends a warm coach message to remind them, a few hours before day_cutoff_time.
    """
    now = datetime.utcnow()
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            # Trigger about 3 hours before cutoff time (e.g. 20:00 if cutoff is 23:00)
            target_hour = (getattr(user, 'day_cutoff_time', time(23, 0)).hour - 3) % 24
            
            if now.hour == target_hour and 0 <= now.minute < 60:
                target_chat_id = user.target_channel_id or user.telegram_id
                
                # Find lagging habits
                habits = db.query(Habit).filter(Habit.user_id == user.id, Habit.nudge_threshold_days > 0).all()
                lagging_habits = []
                for h in habits:
                    last_update = h.updated_at if h.updated_at else h.created_at
                    if last_update:
                        last_update = last_update.replace(tzinfo=None) # naive comparison
                        since_update = (now - last_update).days
                        if since_update >= h.nudge_threshold_days:
                            lagging_habits.append(h.title)
                
                if not lagging_habits:
                    continue
                
                msg_text = "It looks like you've fallen behind on these habits: " + ", ".join(lagging_habits) + "\nPlease remember why you started."
                
                if user.encrypted_google_api_key:
                    try:
                        api_key = decrypt_key(user.encrypted_google_api_key)
                        ai = GoogleProvider(api_key=api_key)
                        prompt = f"The user has fallen behind on these habits for several days: {', '.join(lagging_habits)}. Write a brief, supportive, and pedagogical evening nudge (1-2 sentences) encouraging them to restart without feeling guilty. No markdown."
                        msg_text = run_async(ai.generate_text(prompt))
                    except Exception as e:
                        print(f"Failed to generate AI habit nudge: {e}")
                
                try:
                    if bot:
                        run_async(bot.send_message(chat_id=target_chat_id, text=msg_text))
                except Exception as e:
                    print(f"Failed to send evening nudge to {user.telegram_id}: {e}")

@shared_task(name="job_morning_planner")
def morning_planner_job():
    """
    Runs periodically. Triggers around 9 AM user time.
    Reviews all pending tasks, selects the most impactful 1-3, and sends a gentle
    "Good morning" note encouraging the user to pick one.
    """
    now = datetime.utcnow()
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            import zoneinfo
            try:
                user_tz = zoneinfo.ZoneInfo(user.timezone)
            except Exception:
                user_tz = zoneinfo.ZoneInfo("UTC")
            
            local_time = now.astimezone(user_tz)
            if local_time.hour != 9:
                continue
                
            target_chat_id = user.target_channel_id or user.telegram_id
            
            # Fetch pending tasks
            pending_tasks = db.query(Task).filter(Task.user_id == user.id, Task.status == 'pending').all()
            if not pending_tasks:
                continue
                
            # Clear previous "focus today" flags? We can reset daily.
            for t in pending_tasks:
                t.is_focus_today = False
            
            tasks_list_str = "\\n".join([f"- {t.title}" for t in pending_tasks[:15]])
            
            msg_text = "Good morning! ☀️ You have some tasks lined up. Take a look at your Projects when you're ready."
            if user.api_key_encrypted:
                try:
                    api_key = decrypt_key(user.api_key_encrypted)
                    ai = GoogleProvider(api_key=api_key)
                    prompt = f"The user has these pending tasks:\\n{tasks_list_str}\\n\\nDon't list all of them. Act as a gentle productivity sherpa. Welcome them to a new day. Pick the top 1 or 2 most impactful tasks from the list to suggest as the 'Priority for today'. Keep it conversational, short, and not overwhelming. Ask if they want to start one of those."
                    msg_text = run_async(ai.generate_text(prompt))
                except Exception as e:
                    print(f"Failed to generate morning AI planner: {e}")
            
            db.commit() # Save the cleared focus flags just in case
            
            try:
                if bot:
                    run_async(bot.send_message(chat_id=target_chat_id, text=msg_text, parse_mode="HTML"))
            except Exception as e:
                print(f"Failed to send morning planner to {user.telegram_id}: {e}")
