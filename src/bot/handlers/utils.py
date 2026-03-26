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

def generate_daily_report_text(db, user, force_date: str = None) -> str:
    now = datetime.datetime.utcnow()
    last_24h = now - datetime.timedelta(hours=24)
    
    config = user.report_config
    if isinstance(config, str):
        import json
        try:
            config = json.loads(config)
        except Exception:
            config = None
    if not config:
        config = {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
        
    user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= last_24h).all()
    focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
    void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
    
    proj_stats = {}
    for log in user_logs:
        if log.project_id:
            proj = db.query(Project).filter(Project.id == log.project_id).first()
            if proj:
                if proj.title not in proj_stats:
                    proj_stats[proj.title] = {"minutes": 0, "progress": 0.0, "unit": proj.unit or "minutes"}
                proj_stats[proj.title]["minutes"] += log.duration_minutes
                if log.progress_amount:
                    proj_stats[proj.title]["progress"] += log.progress_amount
    
    user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value} for h in user_habits]
    
    inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
    
    date_str = force_date if force_date else now.strftime("%Y-%m-%d")
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
                persona = getattr(user, "persona_type", "monolith")
                prompt = f"Write a 1-sentence {persona} style comment for this end-of-day report. Just output the sentence."
                response = provider.client.models.generate_content(model=provider.model_id, contents=prompt)
                ai_comment = response.text
            except Exception as e:
                print(f"Failed to generate AI comment: {e}")
                
    report_text = build_daily_report(stats, config, ai_comment)
    return report_text
