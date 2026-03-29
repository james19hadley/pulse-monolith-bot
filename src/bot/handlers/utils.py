from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from src.db.models import User, TokenUsage

def get_or_create_user(db: DBSession, telegram_id: int) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def log_tokens(db: DBSession, telegram_id: int, usage_data: dict):
    if not usage_data: return
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            tu = TokenUsage(
                user_id=user.id,
                prompt_tokens=usage_data.get('prompt_tokens', 0),
                completion_tokens=usage_data.get('completion_tokens', 0),
                total_tokens=usage_data.get('total_tokens', 0),
                model_name=usage_data.get('model_name', 'unknown')
            )
            db.add(tu)
            db.commit()
    except Exception as e:
        print(f"Error logging tokens: {e}")

import datetime
from src.db.models import Project, TimeLog, Habit, Inbox
from src.bot.views import build_daily_report
from src.core.security import decrypt_key
from src.ai.providers import GoogleProvider
from src.core.personas import get_persona_prompt


def get_or_create_project_zero(db: DBSession, user_id: int):
    """Ensures Project 0: Operations exists for the user, creates if needed"""
    from src.db.models import Project
    existing = db.query(Project).filter(
        Project.user_id == user_id,
        Project.title == "Project 0: Operations"
    ).first()
    
    if existing:
        return existing
    
    proj_zero = Project(
        user_id=user_id,
        title="Project 0: Operations",
        status="active",
        target_value=0,
        unit="minutes"
    )
    db.add(proj_zero)
    db.commit()
    db.refresh(proj_zero)
    return proj_zero


def generate_daily_report_text(db, user, force_date: str = None, is_auto_cron: bool = False) -> str:
    now = datetime.datetime.utcnow()
    # Calculate logical day boundaries based on server UTC cutoff
    cutoff_time = getattr(user, 'day_cutoff_time', datetime.time(23, 0))
    today_cutoff = datetime.datetime.combine(now.date(), cutoff_time)
    
    if is_auto_cron:
        if now >= today_cutoff:
            start_bound = today_cutoff - datetime.timedelta(days=1)
            end_bound = today_cutoff
        else:
            start_bound = today_cutoff - datetime.timedelta(days=2)
            end_bound = today_cutoff - datetime.timedelta(days=1)
    else:
        if now < today_cutoff:
            start_bound = today_cutoff - datetime.timedelta(days=1)
            end_bound = today_cutoff
        else:
            start_bound = today_cutoff
            end_bound = today_cutoff + datetime.timedelta(days=1)
    
    config = user.report_config
    if isinstance(config, str):
        import json
        try:
            config = json.loads(config)
        except Exception:
            config = None
    if not config:
        config = {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
        
    user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= start_bound, TimeLog.created_at < end_bound).all()
    focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
    void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
    
    proj_stats = {}
    for log in user_logs:
        if log.project_id:
            proj = db.query(Project).filter(Project.id == log.project_id).first()
            if proj:
                if proj.title not in proj_stats:
                    # Capture the base values for percentage calculation
                    start_val = proj.current_value
                    # We have to subtract the total progress accumulated today to find the start_val of the day, but we don't have that easily here. 
                    # Actually, we can sum the day's progress to find today's percent increase over total.
                    proj_stats[proj.title] = {"minutes": 0, "progress": 0, "unit": proj.unit or "minutes", "target_value": proj.target_value, "current_value": proj.current_value}
                proj_stats[proj.title]["minutes"] += log.duration_minutes
                if log.progress_amount:
                    proj_stats[proj.title]["progress"] += log.progress_amount
    
    user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value, "unit": h.unit or ""} for h in user_habits]
    
    inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
    
    logical_date = start_bound.date()
    date_str = force_date if force_date else logical_date.strftime("%Y-%m-%d")
    stats = {
        "date": date_str,
        "focus_minutes": focus_time,
        "void_minutes": void_time,
        "projects": proj_stats,
        "habits": habits_data,
        "inbox_count": inbox_items
    }
    
    ai_comment = None
    keys = getattr(user, "api_keys", None)
    if keys and user.llm_provider in keys:
        active_key_data = keys[user.llm_provider]
        if active_key_data["provider"] == "google":
            try:
                provider = GoogleProvider(api_key=decrypt_key(active_key_data["key"]))
                persona_sys = get_persona_prompt(user.persona_type, getattr(user, "custom_persona_prompt", None), config)
                
                # Context injection
                import json
                stats_json = json.dumps(stats, ensure_ascii=False)
                context_msg = "The user's day has just automatically ended via chronjob." if is_auto_cron else "The user has manually triggered the end of their day."
                prompt = f"{context_msg} Look at their logged stats: {stats_json}. Write a short 1-2 sentence closing comment in your persona's tone. Mention specific achievements or failures if notable. DO NOT wrap your response in italics. Use Telegram HTML tag <b> to highlight names of specific projects or habits, e.g., <b>Pulse Monolith Bot</b>. NEVER use markdown (**bold**). Just output the sentence, nothing else."
                
                response, tokens = provider.generate_chat_response(prompt, persona_sys)
                if response:
                    ai_comment = response
            except Exception as e:
                print(f"Failed to generate AI comment: {e}")
                
    report_text = build_daily_report(stats, config, ai_comment)
    return report_text
