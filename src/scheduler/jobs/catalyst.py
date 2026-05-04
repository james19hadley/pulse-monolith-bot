"""
Idle session pings (Catalyst Heartbeat).
@Architecture-Map: [JOB-CATALYST]
"""
import asyncio
from datetime import datetime, timedelta
from src.db.repo import SessionLocal
from src.db.models import User, Session as AppSession, TimeLog, Task
from src.bot.texts import Prompts
from src.bot.keyboards.nudge import get_nudge_keyboard
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from celery import shared_task

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
