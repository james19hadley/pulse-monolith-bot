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
                # No Active Session Check
                last_log = db.query(TimeLog).filter(TimeLog.user_id == user.id).order_by(TimeLog.created_at.desc()).first()
                if last_log and (now - last_log.created_at) > timedelta(minutes=60):
                    pending_tasks = db.query(Task).filter_by(user_id=user.id, status='pending').count()
                    if pending_tasks == 0:
                        last_event_time = last_log.created_at
                        is_ping_due = True
                        ping_text = Prompts.NUDGE_ZERO_TASKS
                    elif (now - last_log.created_at) > timedelta(minutes=180): 
                        # Proactive push if they have tasks but haven't worked in 3+ hours
                        last_event_time = last_log.created_at
                        is_ping_due = True
                        ping_text = "Hey, you have pending tasks but haven't logged any work in a few hours. Ready to tackle one?"

            has_active_session = session is not None

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
                        persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config, getattr(user, "talkativeness_level", "standard"))
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
                        # Only send buttons (Retroactive End/Finish) if the user is ACTUALLY in a session.
                        # If they are just being prodded to start working, send NO buttons (they just reply).
                        reply_markup = get_nudge_keyboard() if has_active_session else None
                        
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=ping_text, 
                            parse_mode="HTML",
                            reply_markup=reply_markup
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


@shared_task(name="job_evening_reflection")
def evening_reflection_job():
    """Runs at 21:00 user local time to trigger an evening reflection."""
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
            
            # Request from user: Evening reflection should be explicitly at 21:00 local time
            # Using < 15 matches the */15 Celery beat schedule to guarantee exactly 1 execution
            is_time = False
            if local_time.hour == 21 and 0 <= local_time.minute < 15:
                is_time = True
            
            if is_time:
                msg_text = "It is almost the end of the day. What did you get done, and what's the plan for tomorrow?"
                user_keys = getattr(user, "api_keys", None)
                if user_keys and user.llm_provider in user_keys:
                    try:
                        key_data = user_keys[user.llm_provider]
                        ai = GoogleProvider(api_key=decrypt_key(key_data["key"]))
                        from src.core.personas import get_persona_prompt
                        persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config, getattr(user, "talkativeness_level", "standard"))
                        user_lang = getattr(user, "language", "Russian")
                        
                        ref_config = getattr(user, 'reflection_config', {}) or {}
                        wins = "Ask them about their wins/achievements today. " if ref_config.get("focus_wins") else ""
                        blockers = "Ask them about any blockers or problems they faced today. " if ref_config.get("focus_blockers") else ""
                        tomorrow = "Ask them what they want to plan for tomorrow. " if ref_config.get("focus_tomorrow") else ""
                        custom = f"Also incorporate this specific focus into your question: '{ref_config.get('custom_prompt')}'. " if ref_config.get("custom_prompt") else ""
                        
                        topics = wins + blockers + tomorrow + custom
                        if not topics:
                            topics = "Ask them how the day went overall."
                            
                        # Sprint 44: Task Engine & Inbox Converter
                        from src.db.models import Inbox
                        pending_inbox = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
                        if pending_inbox > 0:
                            topics += f"\nCRITICAL: Mention that they captured {pending_inbox} items in their inbox. Ask them if they want to delete them or convert them into Actionable Tasks for tomorrow (and ask when they want to do them: morning, afternoon, etc)."
                        
                        prompt = f"Initiate an evening reflection session with the user. Inform them that the day is wrapping up (approaching their {cutoff.strftime('%H:%M')} cutoff). {topics} DO NOT USE MARKDOWN. Use HTML tags <b> and <i> only. Must strictly speak in {user_lang}. Do not write a long paragraph unless talkativeness is set to coach."
                        
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

@shared_task(name="job_task_reminders_watchdog")
def task_reminders_watchdog_job():
    """
    Runs every 5 minutes to check for pending tasks that have a reminder_time <= now.
    """
    import zoneinfo
    import html
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
            
            from src.db.models import Task
            # Find tasks where reminder_time is not null, hasn't been sent, and time has passed
            pending_reminders = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status == 'pending',
                Task.is_reminder_sent == False,
                Task.reminder_time != None,
                Task.reminder_time <= local_time
            ).all()
            
            for task in pending_reminders:
                try:
                    target_chat_id = user.target_channel_id or user.telegram_id
                    msg = f"⏰ <b>Напоминание:</b> {html.escape(task.title)}"
                    if bot:
                        run_async(bot.send_message(chat_id=target_chat_id, text=msg, parse_mode="HTML"))
                    task.is_reminder_sent = True
                except Exception as e:
                    print(f"Failed to send task reminder to {user.telegram_id}: {e}")
                    
        db.commit()

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
            
            # Continuity check: Did they say something yesterday evening?
            evening_plan_text = ""
            if getattr(user, 'last_evening_plan', None):
                evening_plan_text = f"\n\nLast night, the user shared this plan/reflection:\n\"{user.last_evening_plan}\"\n\nPlease reference this gracefully in your morning welcome."
                user.last_evening_plan = None # Clear it for the new day
            
            tasks_list_str = "\\n".join([f"- {t.title}" for t in pending_tasks[:15]])
            
            msg_text = "Good morning! ☀️ You have some tasks lined up. Take a look at your Projects when you're ready."
            user_keys = getattr(user, "api_keys", None)
            if user_keys and user.llm_provider in user_keys:
                try:
                    key_data = user_keys[user.llm_provider]
                    ai = GoogleProvider(api_key=decrypt_key(key_data["key"]))
                    from src.core.personas import get_persona_prompt
                    persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config, getattr(user, "talkativeness_level", "standard"))
                    
                    user_lang = getattr(user, "language", "Russian")
                    prompt = f"The user has these pending tasks:\\n{tasks_list_str}{evening_plan_text}\\n\\nDon't list all of them. Welcome them to a new day. Pick the top 1 or 2 most impactful tasks from the list to suggest as the 'Priority for today'. Keep it conversational. Ask if they want to start one of those. Must strictly speak in {user_lang}. DO NOT USE MARKDOWN. Use HTML tags <b> and <i> only."
                    
                    res, _ = ai.generate_chat_response(prompt, persona_prompt=persona_sys)
                    if res:
                        msg_text = res
                except Exception as e:
                    print(f"Failed to generate morning AI planner: {e}")
            
            db.commit() # Save the cleared focus flags and cleared evening plan
            
            try:
                if bot:
                    run_async(bot.send_message(chat_id=target_chat_id, text=msg_text, parse_mode="HTML"))
            except Exception as e:
                print(f"Failed to send morning planner to {user.telegram_id}: {e}")


