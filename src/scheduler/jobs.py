import os
import asyncio
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from src.db.repo import SessionLocal
from src.db.models import User, Session as AppSession, TimeLog, Habit, Inbox, Project
from aiogram import Bot

from src.bot.views import catalyst_ping_message, stale_session_closed_message, build_daily_report
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
        active_sessions = db.query(AppSession).filter(AppSession.status == "active").all()
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
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id]))
                    except Exception:
                        pass
                
                hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                try:
                    if bot:
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=catalyst_ping_message(hours_idle)
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
        active_sessions = db.query(AppSession).filter(AppSession.status == "active").all()
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
                
                # Default config fallback
                config = user.report_config if user.report_config else {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
                target_chat_id = user.target_channel_id or user.telegram_id
                
                # Gather stats for the last 24 hours
                last_24h = now - timedelta(hours=24)
                
                # Get logs
                user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= last_24h).all()
                focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
                void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
                
                proj_stats = {}
                for log in user_logs:
                    if log.project_id:
                        proj = db.query(Project).filter(Project.id == log.project_id).first()
                        p_title = proj.title if proj else "Unknown Project"
                        proj_stats[p_title] = proj_stats.get(p_title, 0) + log.duration_minutes
                
                # Get habits
                user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
                habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value} for h in user_habits]
                
                # Get inbox
                inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
                
                stats = {
                    "date": now.strftime("%Y-%m-%d"),
                    "focus_minutes": focus_time,
                    "void_minutes": void_time,
                    "projects": proj_stats,
                    "habits": habits_data,
                    "inbox_count": inbox_items
                }
                
                # AI Chef's Kiss Generation
                ai_comment = None
                keys = user.api_keys
                if keys and user.llm_provider in keys and user.llm_provider == "google":
                    try:
                        from src.core.personas import get_persona_prompt
                        provider = GoogleProvider(api_key=decrypt_key(keys[user.llm_provider]))
                        
                        # Use the new persona engine for consistency
                        persona_sys = get_persona_prompt(user.persona_type, user.custom_persona_prompt, config)
                        prompt = "The user's day has ended. Look at their logged stats (if any) and write a short 1-2 sentence closing comment in your persona's tone. It will be appended to the bottom of their daily markdown report. Just output the sentence, nothing else."
                        
                        response, _tokens = provider.generate_chat_response(prompt, persona_sys)
                        if response:
                            ai_comment = response
                    except Exception as e:
                        print(f"Failed to generate AI comment: {e}")
                
                # Build report via views
                report_text = build_daily_report(stats, config, ai_comment)
                
                if bot:
                    try:
                        run_async(bot.send_message(
                            chat_id=target_chat_id,
                            text=report_text,
                            parse_mode="HTML"
                        ))
                    except Exception as e:
                        print(f"Failed to send accountability report to {target_chat_id}: {e}")
