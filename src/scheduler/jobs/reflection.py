"""
Evening reflection nudge generation.
@Architecture-Map: [JOB-REFLECT]
"""
from datetime import datetime, time
from src.db.repo import SessionLocal
from src.db.models import User, Inbox
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from src.ai.providers import GoogleProvider
from src.core.security import decrypt_key
from celery import shared_task

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
