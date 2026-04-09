"""
Utility bot handlers (e.g. callback query cleaners, generic paginations).

@Architecture-Map: [HND-UTILS]
@Docs: docs/07_ARCHITECTURE_MAP.md
"""
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
from src.db.models import Project, TimeLog, Inbox
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
        config = {"blocks": ["focus", "projects", "inbox"], "style": "emoji"}
        
    user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= start_bound, TimeLog.created_at < end_bound).all()
    focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
    
    # Pre-calculate global total progress for display correctness
    from sqlalchemy import func
    global_progress = dict(db.query(TimeLog.project_id, func.sum(TimeLog.progress_amount)).filter(TimeLog.user_id == user.id).group_by(TimeLog.project_id).all())
    
    # Build project stats with hierarchy
    all_projects = {p.id: p for p in db.query(Project).filter(Project.user_id == user.id).all()}
    
    # 1. Aggregate raw logs
    raw_stats = {}
    for log in user_logs:
        if log.project_id and log.project_id in all_projects:
            pid = log.project_id
            if pid not in raw_stats:
                raw_stats[pid] = {"minutes": 0, "progress": 0}
            raw_stats[pid]["minutes"] += log.duration_minutes
            if log.progress_amount:
                raw_stats[pid]["progress"] += log.progress_amount
                
    # 2. Bubble up minutes to parents (only 1 level deep as per spec: Epic -> Main Quest isn't fully enforced but we handle 2 levels via parent_id)
    parent_totals = {}
    for pid, data in raw_stats.items():
        node = all_projects[pid]
        curr = node
        visited = set()
        while curr.parent_id and curr.parent_id in all_projects and curr.id not in visited:
            visited.add(curr.id)
            parent = all_projects[curr.parent_id]
            if parent.id not in parent_totals:
                parent_totals[parent.id] = {"minutes": 0}
            parent_totals[parent.id]["minutes"] += data["minutes"]
            curr = parent
            
    # Combine
    combined = set(raw_stats.keys()).union(set(parent_totals.keys()))

    # Build tree representation
    roots = [pid for pid in combined if not all_projects[pid].parent_id]
    roots.sort(key=lambda pid: (0 if all_projects[pid].title.startswith("Project 0") else 1, all_projects[pid].title))
    
    proj_stats = {} 
    
    def add_node(pid, indent_level):
        p = all_projects[pid]
        self_mins = raw_stats.get(pid, {}).get("minutes", 0)
        bubble_mins = parent_totals.get(pid, {}).get("minutes", 0)
        total_mins = self_mins + bubble_mins
        
        proj_stats[p.title] = {
            "minutes": total_mins,
            "progress": raw_stats.get(pid, {}).get("progress", 0),
            "unit": p.unit or "minutes",
            "target_value": p.target_value or 0,
            "current_value": global_progress.get(pid) or p.current_value or 0,
            "indent": indent_level
        }
        
        # add children
        children = [c_id for c_id in combined if all_projects[c_id].parent_id == pid]
        children.sort(key=lambda c: all_projects[c].title)
        for c in children:
            add_node(c, indent_level + 1)
            
    for r in roots:
        add_node(r, 0)
    user_habits = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None).all()
    habits_data = [{"title": h.title, "current": h.daily_progress or 0, "target": h.daily_target_value, "unit": h.unit or ""} for h in user_habits]
    
    inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
    
    logical_date = start_bound.date()
    date_str = force_date if force_date else logical_date.strftime("%Y-%m-%d")
    stats = {
        "date": date_str,
        "focus_minutes": focus_time,
        "projects": proj_stats,
        "projects_daily": habits_data,
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
                user_lang = getattr(user, 'language', 'Russian') or 'Russian'
                prompt = f"{context_msg} Look at their logged stats: {stats_json}. Write a short 1-2 sentence closing comment in your persona's tone. Mention specific achievements or failures if notable. NOTE IMPORTANT: You must respond in the user's explicit language: {user_lang}. DO NOT wrap your response in italics. Use Telegram HTML tag <b> to highlight names of specific projects or habits, e.g., <b>Pulse Monolith Bot</b>. NEVER use markdown (**bold**). Just output the sentence, nothing else."
                
                response, tokens = provider.generate_chat_response(prompt, persona_sys)
                if response:
                    ai_comment = response
            except Exception as e:
                print(f"Failed to generate AI comment: {e}")
                
    report_text = build_daily_report(stats, config, ai_comment)
    return report_text
