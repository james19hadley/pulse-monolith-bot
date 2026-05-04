from datetime import datetime
from src.db.repo import SessionLocal
from src.db.models import User, Task
from src.scheduler.tasks import run_async
from src.scheduler.jobs.base import bot
from src.ai.providers import GoogleProvider
from src.core.security import decrypt_key
from celery import shared_task

@shared_task(name="job_morning_planner")
def morning_planner_job():
    """
    Pulls pending DB tasks and spoon-feeds priority items to the AI for a curated morning message.
    
    @Architecture-Map: [JOB-MORN-PLAN]
    @Docs: docs/reference/07_ARCHITECTURE_MAP.md
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
            
            tasks_list_str = "\\n".join([f"- {t.title} ({getattr(t, 'estimated_minutes', 0) or 0}m)" for t in pending_tasks[:15]])
            total_est_minutes = sum([getattr(t, 'estimated_minutes', 0) or 0 for t in pending_tasks])
            est_hours = total_est_minutes // 60
            est_mins = total_est_minutes % 60
            dur_str = f"{est_hours}h {est_mins}m" if est_hours > 0 else f"{est_mins}m"
            
            msg_text = "Good morning! ☀️ You have some tasks lined up. Take a look at your Projects when you're ready."
            user_keys = getattr(user, "api_keys", None)
            if user_keys and user.llm_provider in user_keys:
                try:
                    key_data = user_keys[user.llm_provider]
                    ai = GoogleProvider(api_key=decrypt_key(key_data["key"]))
                    from src.core.personas import get_persona_prompt
                    persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), user.report_config, getattr(user, "talkativeness_level", "standard"))
                    
                    user_lang = getattr(user, "language", "Russian")
                    prompt = f"The user has these pending tasks (Total estimated workload: {dur_str}):\\n{tasks_list_str}{evening_plan_text}\\n\\nDon't list all of them. Welcome them to a new day. Pick the top 1 or 2 most impactful tasks from the list to suggest as the 'Priority for today'. Keep it conversational. Mention their total estimated workload if it's significant (>0m). Ask if they want to start one of those. Must strictly speak in {user_lang}. DO NOT USE MARKDOWN. Use HTML tags <b> and <i> only."
                    
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
