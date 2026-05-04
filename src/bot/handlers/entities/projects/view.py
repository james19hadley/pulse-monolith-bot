"""
Project view rendering logic.
@Architecture-Map: [HND-PROJ-VIEW]
"""
from datetime import datetime, timezone, time
from sqlalchemy.orm import Session
from src.db.models import Project, TimeLog, Task
from src.bot.keyboards import get_project_view_keyboard

async def render_project_view(cb, db: Session, user, proj: Project):
    """
    Renders the detailed project view with stats, progress bar, and tasks.
    """
    # Recursive function to get all sub-project IDs
    def get_all_child_ids(p_id):
        children = db.query(Project.id).filter(Project.parent_id == p_id).all()
        res = []
        for c in children:
            res.append(c[0])
            res.extend(get_all_child_ids(c[0]))
        return res
        
    all_ids = [proj.id] + get_all_child_ids(proj.id)
    
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    
    # Logs for THIS project only (for progress units like pages)
    direct_logs = db.query(TimeLog).filter(TimeLog.project_id == proj.id).all()
    
    # Logs for ENTIRE tree (for total HOURS bubbled up)
    tree_logs = db.query(TimeLog).filter(TimeLog.project_id.in_(all_ids)).all()
    
    total_minutes = sum([l.duration_minutes for l in tree_logs])
    today_minutes = sum([l.duration_minutes for l in tree_logs if l.created_at >= today_start])
    
    now_dt = datetime.now(timezone.utc)
    last_active_str = "Never"
    if tree_logs:
        last_log_dt = max(l.created_at for l in tree_logs).replace(tzinfo=timezone.utc)
        diff = now_dt - last_log_dt
        if diff.total_seconds() < 3600:
            last_active_str = f"{int(diff.total_seconds() // 60)} mins ago"
        elif diff.total_seconds() < 86400:
            last_active_str = f"{int(diff.total_seconds() // 3600)} hours ago"
        else:
            last_active_str = f"{diff.days} days ago"

    today_progress = sum([l.progress_amount or 0 for l in direct_logs if l.created_at >= today_start and l.progress_amount])
    total_progress = sum([l.progress_amount or 0 for l in direct_logs if l.progress_amount])

    total_hours = total_minutes / 60
    today_hours = today_minutes / 60
    
    is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']

    progress_bar = ""
    if proj.target_value > 0:
        if is_time_based:
            pct = min(1.0, (total_minutes / proj.target_value) if proj.target_value else 0)
        else:
            pct = min(1.0, (total_progress / proj.target_value) if proj.target_value else 0)
        filled = int(pct * 10)
        progress_bar = "\nProgress: [" + "█" * filled + "░" * (10 - filled) + f"] {pct*100:.1f}%\n"
        
    if is_time_based:
        hours = proj.target_value / 60 if proj.target_value > 0 else 0
        text = f"📁 <b>{proj.title}</b>\n\nTarget Hours: {hours:g}h\nTotal Tracked: {total_hours:g}h\nToday Tracked: {today_hours:g}h\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
    else:
        text = f"📁 <b>{proj.title}</b>\n\nTarget: {proj.target_value:g} {proj.unit}\nTotal Progress: {total_progress:g} {proj.unit}\nToday Progress: {today_progress:g} {proj.unit}\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"

    if getattr(proj, 'daily_target_value', None) is not None:
        streak = getattr(proj, 'current_streak', 0)
        daily_prog = getattr(proj, 'daily_progress', 0)
        emoji = "🔥" if streak > 0 else "🎯"
        text += f"\n{emoji} Daily Target: {daily_prog:g} / {proj.daily_target_value:g} {proj.unit or 'min'}"
        if streak > 0:
            text += f" (Streak: {streak} days)"

    pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(5).all()
    if pending_tasks:
        text += "\n\n📋 <b>Next Tasks:</b>\n"
        for i, t in enumerate(pending_tasks, 1):
            prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
            text += f"{i}. {prefix}{t.title}\n"
        
    sub_count = db.query(Project).filter(Project.parent_id == proj.id, Project.status != "deleted").count()
    parent_id = proj.parent_id
    if parent_id:
        parent = db.query(Project).filter(Project.id == parent_id).first()
        if parent:
            text = text.replace(f"📁 <b>{proj.title}</b>", f"📂 <b>{parent.title} ➡ {proj.title}</b>")
    
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id, status=proj.status, sub_count=sub_count, parent_id=parent_id))
    except Exception as e:
        if "message is not modified" not in str(e):
            raise e
