"""
Logic for adding tasks with estimated times and reminders via AI intents.
@Architecture-Map: [HND-INTENT-ENT-TASK]
"""
import html
import zoneinfo
from datetime import datetime, timezone
from aiogram.types import Message
from dateutil import parser
from src.db.models import Project, Task, Inbox
from src.ai.router import extract_add_tasks
from src.bot.handlers.utils import log_tokens
from src.bot.handlers.spinner import ProcessingSpinner

async def handle_add_tasks(message: Message, db, user, provider_name, api_key):
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    projects_text = "Active Projects:\n" + "\n".join([f"- {p.title} (ID: {p.id})" for p in projects]) if projects else "No active projects."
    
    try:
        user_tz = zoneinfo.ZoneInfo(user.timezone)
    except Exception:
        user_tz = zoneinfo.ZoneInfo("UTC")
    local_now = datetime.now(timezone.utc).astimezone(user_tz)
    projects_text += f"\n\nCURRENT LOCAL TIME FOR USER: {local_now.isoformat()}"
    
    spinner = ProcessingSpinner(message, "🧠 Извлекаю параметры задач (может занять время)...")
    await spinner.start()
    
    try:
        # Extract tasks
        extraction, tokens = await extract_add_tasks(message.text, provider_name, api_key, projects_text)
    finally:
        await spinner.stop()
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not extraction.tasks:
        await message.answer("I couldn't identify any tasks to add.")
        return
        
    msg_lines = []
    count = 0
    scheduled_tasks = []
    
    for t in extraction.tasks:
        parsed_reminder_time = None
        raw_rt = getattr(t, 'reminder_time', None)
        if raw_rt:
            try:
                parsed_reminder_time = parser.parse(raw_rt)
            except Exception as e:
                print(f"Could not parse reminder_time '{raw_rt}': {e}")
                
        # Create Task
        new_task = Task(
            user_id=user.id,
            title=t.title,
            project_id=t.project_id if t.project_id else None,
            status='pending',
            estimated_minutes=getattr(t, 'estimated_minutes', None),
            reminder_time=parsed_reminder_time
        )
        db.add(new_task)
        db.flush()
        
        if new_task.reminder_time:
            scheduled_tasks.append((new_task.id, new_task.reminder_time))
            
        count += 1
        
        proj_name = "Inbox"
        if t.project_id:
            db_proj = db.query(Project).filter(Project.id == t.project_id).first()
            if db_proj:
                proj_name = db_proj.title
        
        time_str = f" ⏰ <i>{t.reminder_time}</i>" if getattr(t, 'reminder_time', None) else ""
        dur_str = f" ⏳ {t.estimated_minutes}m" if getattr(t, 'estimated_minutes', None) else ""
        msg_lines.append(f"• {t.title}{dur_str}{time_str} 📂 <i>{html.escape(proj_name)}</i>")
        
    db.commit()
    
    # Schedule Celery ETA tasks if any
    if scheduled_tasks:
        from src.scheduler.jobs import send_task_reminder_job
        for tid, rtime in scheduled_tasks:
            try:
                send_task_reminder_job.apply_async(args=[tid], eta=rtime)
            except Exception as e:
                print(f"Failed to queue reminder for task {tid}: {e}")
    
    extra_msg = ""
    if getattr(extraction, 'clear_inbox', False):
        cleared = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").update({"status": "cleared"})
        db.commit()
        if cleared > 0:
            extra_msg = f"\n🧹 <i>(Cleared {cleared} items from Inbox)</i>"
    
    nl = '\n'
    await message.answer(f"✅ <b>Added {count} task(s):</b>\n{nl.join(msg_lines)}{extra_msg}", parse_mode="HTML")
