import os
from src.bot.keyboards.nudge import get_nudge_keyboard
from src.bot.texts import Prompts
import asyncio
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from src.db.repo import SessionLocal
from src.db.models import User, Session as AppSession, TimeLog, Inbox, Project, Task, Task
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
    Zero Tasks: if no active session and idle for > 1hr with 0 tasks, sends a ping.
    """
    with SessionLocal() as db:
        users = db.query(User).all()
        now = datetime.utcnow()
        for user in users:
            telegram_id = user.telegram_id
            threshold_minutes = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes is not None else 60
            interval_minutes = user.catalyst_interval_minutes if user.catalyst_interval_minutes is not None else 20
            
            if threshold_minutes <= 0:
                continue

            session = db.query(AppSession).filter(AppSession.user_id == user.id, AppSession.status.in_(["active", "rest"])).first()
            is_ping_due = False
            ping_text = ""
            last_event_time = now

            if session:
                last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
                idle_since = last_log.created_at if last_log else session.start_time
                if session.status == "active":
                    if now - idle_since > timedelta(minutes=threshold_minutes):
                        hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                        is_ping_due = True
                        ping_text = Prompts.NUDGE_ACTIVE_SESSION.format(hours_idle=hours_idle)
                        last_event_time = idle_since
                elif session.status == "rest":
                    if session.rest_start_time and (now - session.rest_start_time > timedelta(minutes=30)):
                        mins_rested = int((now - session.rest_start_time).total_seconds() / 60)
                        is_ping_due = True
                        ctx_text = f" Твой Save-State: «{session.save_state_context}»." if session.save_state_context else ""
                        ping_text = Prompts.NUDGE_REST_SESSION.format(mins_rested=mins_rested, ctx_text=ctx_text)
                        last_event_time = session.rest_start_time
            else:
                # Zero Tasks Check
                last_log = db.query(TimeLog).filter(TimeLog.user_id == user.id).order_by(TimeLog.created_at.desc()).first()
                if last_log and (now - last_log.created_at) > timedelta(minutes=60):
                    pending_tasks = db.query(Task).filter_by(user_id=user.id, status='pending').count()
                    if pending_tasks == 0:
                        last_event_time = last_log.created_at
                        is_ping_due = True
                        ping_text = Prompts.NUDGE_ZERO_TASKS

            if is_ping_due:
                # Intercept with AI generation if API keys exist
                user_keys = getattr(user, "api_keys", None)
                if user_keys and user.llm_provider in user_keys:
                    try:
                        key_data = user_keys[user.llm_provider]
                        from src.ai.providers import GoogleProvider
                        from src.core.security import decrypt_key
                        from src.core.personas import get_persona_prompt
                        
                        ai = GoogleProvider(api_key=decrypt_key(key_data["key"]))
                        persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config)
                        user_lang = getattr(user, "language", "Russian")
                        prompt = f"The user is currently idle. Here is the context: '{ping_text}'. Send them a very short Catalyst Nudge (1-2 sentences) encouraging them to log their time or update their status. Speak purely in {user_lang}. DO NOT USE MARKDOWN, only <b> and <i>."
                        text, _ = ai.generate_chat_response(prompt, persona_sys)
                        if text:
                            ping_text = text
                    except Exception as e:
                        print(f"Failed to generate AI catalyst ping: {e}")
                
                last_ping_time = last_ping_timestamps.get(telegram_id)
                already_pinged = (last_ping_time is not None and last_ping_time >= last_event_time)
                
                if interval_minutes <= 0 and already_pinged:
                    continue
                if interval_minutes > 0 and already_pinged:
                    if (now - last_ping_time) < timedelta(minutes=interval_minutes):
                        continue

                # Clean up existing message using the DB value!
                if user.last_ping_message_id:
                    try:
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=user.last_ping_message_id))
                    except Exception:
                        pass
                elif telegram_id in last_ping_message_ids: # Fallback old in-memory
                    try:
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id]))
                    except Exception:
                        pass
                
                try:
                    if bot:
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=ping_text, reply_markup=get_nudge_keyboard()
                        ))
                        last_ping_message_ids[telegram_id] = msg.message_id
                        user.last_ping_message_id = msg.message_id
                        last_ping_timestamps[telegram_id] = now
                        db.commit()
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
            if local_time.hour == cutoff.hour and local_time.minute == cutoff.minute and not already_done: # Precise execution for odd timezones! # Runs once an hour roughly
                
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

                # End of Day Reset: Explicitly after the daily report generation!
                try:
                    projects = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None).all()
                    for p in projects:
                        if (p.daily_progress or 0) < p.daily_target_value:
                            p.current_streak = 0
                        p.daily_progress = 0
                    db.commit()
                except Exception as e:
                    print(f"Failed to reset daily stats for user {user.telegram_id}: {e}")
                    db.rollback()


@shared_task(name="job_evening_reflection")
def evening_reflection_job():
    """Runs 30 minutes before day_cutoff_time to trigger an evening reflection."""
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
            cutoff = getattr(user, 'day_cutoff_time', time(23, 0))
            
            # Check if it is EXACTLY 30 minutes before cutoff (hour matching)
            is_time = False
            if cutoff.minute >= 30:
                if local_time.hour == cutoff.hour and local_time.minute == cutoff.minute - 30:
                    is_time = True
            else:
                target_hour = (cutoff.hour - 1) % 24
                target_minute = 60 + cutoff.minute - 30
                if local_time.hour == target_hour and local_time.minute == target_minute:
                    is_time = True
            
            if is_time:
                msg_text = "It is almost the end of the day. What targets did you hit today, and what is your plan for tomorrow? Tell me naturally, and I will log it for you."
                user_keys = getattr(user, "api_keys", None)
                if user_keys and user.llm_provider in user_keys:
                    try:
                        key_data = user_keys[user.llm_provider]
                        ai = GoogleProvider(api_key=decrypt_key(key_data["key"]))
                        from src.core.personas import get_persona_prompt
                        persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config)
                        user_lang = getattr(user, "language", "Russian")
                        prompt = f"Initiate an evening reflection session with the user. Inform them that the day is almost over (their cutoff is {cutoff.strftime("%H:%M")}). Ask them what project targets they achieved today and what they want to plan for tomorrow so you can passively log it. DO NOT USE MARKDOWN. Use HTML tags <b> and <i> only. Must strictly speak in {user_lang}. Limit to 2 short sentences."
                        text, _ = ai.generate_chat_response(prompt, persona_sys)
                        if text:
                            msg_text = text
                    except Exception as e:
                        print(f"Failed to generate reflection prompt: {e}")
                
                try:
                    if bot:
                        run_async(bot.send_message(chat_id=user.telegram_id, text=msg_text, parse_mode="HTML"))
                except Exception as e:
                    print(f"Failed to send reflection ping to {user.telegram_id}: {e}")
@shared_task(name="job_morning_planner")
def morning_planner_job():
    """
    Pulls pending DB tasks and spoon-feeds priority items to the AI for a curated morning message.
    
    @Architecture-Map: [JOB-MORN-PLAN]
    @Docs: docs/reference/07_ARCHITECTURE_MAP.md
    """
    """
    Runs periodically. Triggers around 9 AM user time.
    Reviews all pending tasks, selects the most impactful 1-3, and sends a gentle
    "Good morning" note encouraging the user to pick one.
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
            if local_time.hour != 9:
                continue
            # Morning planner is a private coach, send strictly to DM
            target_chat_id = user.telegram_id
            
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
                    res, _ = ai.generate_chat_response(prompt, persona_prompt="You are a gentle productivity coach.")
                    if res:
                        msg_text = res
                except Exception as e:
                    print(f"Failed to generate morning AI planner: {e}")
            
            db.commit() # Save the cleared focus flags just in case
            
            try:
                if bot:
                    run_async(bot.send_message(chat_id=target_chat_id, text=msg_text, parse_mode="HTML"))
            except Exception as e:
                print(f"Failed to send morning planner to {user.telegram_id}: {e}")


