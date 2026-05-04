"""
Processing AI-parsed entity creation intents (Project, Quest, Habit).

@Architecture-Map: [HND-INTENT-ENT]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import Message
from sqlalchemy import func
from src.ai.router import extract_entities, extract_inbox, extract_add_tasks, extract_edit_entities
from src.bot.handlers.utils import log_tokens
async def _handle_create_entities(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project
    
    active_projs = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
    active_projects_text = "\n".join([f"[{p.id}] {p.title}" for p in active_projs])
    
    extraction, tokens = await extract_entities(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or (not extraction.projects and not extraction.habits):
        await message.answer("I could not determine the exact details for the project to create.")
        return
        
    responses = []
    
    from sqlalchemy import func
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    for p in extraction.projects:
        existing = db.query(Project).filter(Project.user_id == user.id, func.lower(Project.title) == p.title.lower()).first()
        if existing:
            if existing.status == "archived":
                existing.status = "active"
                if getattr(p, 'lifetime_target_value', 0) > 0:
                    existing.target_value = p.lifetime_target_value
                if getattr(p, 'periodic_target_value', None) is not None:
                    existing.daily_target_value = p.periodic_target_value
                if getattr(p, 'target_period', None):
                    existing.target_period = p.target_period
                if hasattr(p, 'unit') and p.unit:
                    existing.unit = p.unit
                db.commit()
                # Log action for SMART UNDO
                from src.db.models import ActionLog
                import json
                alog = ActionLog(user_id=user.id, tool_name="create_project", previous_state_json={"status": "archived", "target_value": existing.target_value}, new_state_json={"project_id": existing.id, "status": "active"})
                db.add(alog)
                db.commit()
                
                msg = f"✅ Project restored from archive: <b>{existing.title}</b>"
                if existing.target_value > 0:
                    msg += f" (Lifetime Target: {existing.target_value})"
                if existing.daily_target_value:
                    msg += f" ({existing.target_period.capitalize()} Target: {existing.daily_target_value})"
                if hasattr(existing, 'unit') and existing.unit:
                    msg += f" {existing.unit}"
                await message.answer(msg, parse_mode="HTML")
            else:
                await message.answer(f"⚠️ Project already exists: <b>{existing.title}</b>", parse_mode="HTML")
            continue
            
        proj = Project(
            user_id=user.id,
            title=p.title,
            status="active",
            target_value=getattr(p, 'lifetime_target_value', 0),
            daily_target_value=getattr(p, 'periodic_target_value', None),
            target_period=getattr(p, 'target_period', 'daily') or 'daily'
        )
        if hasattr(p, 'unit') and p.unit:
            proj.unit = p.unit
        if hasattr(p, 'parent_project_id') and p.parent_project_id:
            parent = db.query(Project).filter(Project.id == p.parent_project_id, Project.user_id == user.id).first()
            if parent:
                proj.parent_id = parent.id
        db.add(proj)
        db.flush()
        
        # Log action for SMART UNDO
        from src.db.models import ActionLog
        import json
        alog = ActionLog(user_id=user.id, tool_name="create_project", previous_state_json={}, new_state_json={"project_id": proj.id})
        db.add(alog)
        
        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            if getattr(proj, 'unit', None) and proj.unit not in ['minutes', 'hours']:
                msg += f" (Target: {proj.target_value} {proj.unit})"
            else:
                msg += f" (Target: {proj.target_value / 60:g}h)"
        if getattr(proj, 'parent_id', None):
            parent = db.query(Project).filter(Project.id == proj.parent_id).first()
            msg += f"\n📂 Attached to parent: <b>{parent.title}</b>"
        await message.answer(msg, parse_mode="HTML")
        
    # Log action for SMART UNDO
        from src.db.models import ActionLog
        import json
        db.add(alog)
        
        
    db.commit()


async def _handle_add_inbox(message: Message, db, user, provider_name, api_key):
    from src.db.models import Inbox
    from src.bot.handlers.utils import log_tokens
    
    extraction, tokens = await extract_inbox(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not getattr(extraction, "raw_content", None):
        await message.answer("I could not determine what to save to your inbox.")
        return
        
    inbox_item = Inbox(user_id=user.id, raw_text=extraction.raw_content, status="pending")
    db.add(inbox_item)
    db.commit()
    
    import html
    safe_text = html.escape(extraction.raw_content)
    await message.answer(f"📥 <b>Saved to Inbox:</b>\n<i>{safe_text}</i>", parse_mode="HTML")




async def _handle_add_tasks(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Task
    from src.ai.router import extract_add_tasks
    import html
    from src.bot.handlers.utils import log_tokens
    
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    projects_text = "Active Projects:\n" + "\n".join([f"- {p.title} (ID: {p.id})" for p in projects]) if projects else "No active projects."
    
    import zoneinfo
    from datetime import datetime, timezone
    try:
        user_tz = zoneinfo.ZoneInfo(user.timezone)
    except Exception:
        user_tz = zoneinfo.ZoneInfo("UTC")
    local_now = datetime.now(timezone.utc).astimezone(user_tz)
    projects_text += f"\n\nCURRENT LOCAL TIME FOR USER: {local_now.isoformat()}"
    
    from src.bot.handlers.spinner import ProcessingSpinner
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
        
    responses = []
    msg_lines = []
    count = 0
    from src.db.models import ActionLog
    
    scheduled_tasks = []
    
    from dateutil import parser
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
        # Flush to get the ID without committing the whole transaction yet
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
        from src.db.models import Inbox
        cleared = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").update({"status": "cleared"})
        db.commit()
        if cleared > 0:
            extra_msg = f"\n🧹 <i>(Cleared {cleared} items from Inbox)</i>"
    
    nl = '\n'
    await message.answer(f"✅ <b>Added {count} task(s):</b>\n{nl.join(msg_lines)}{extra_msg}", parse_mode="HTML")

async def _handle_edit_entities(message: Message, db, user, provider_name, api_key):

    from src.db.models import Project, Task
    
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    entities_list = []
    for p in projects:
        entities_list.append(f"Project: {p.title} (ID: {p.id})")
        
    tasks = db.query(Task).filter(Task.user_id == user.id, Task.status == 'pending').all()
    for idx, t in enumerate(tasks, 1):
        entities_list.append(f"Task {idx}: {t.title} (DB_ID: {t.id})")
    
    if not entities_list:
        await message.answer("You have no projects or tasks to edit yet.")
        return
    
    entities_text = "Your entities (Tasks have ordinal numbers for UX, but MUST be referenced by DB_ID):\n" + "\n".join(entities_list)
    
    # Extract edit requests
    extraction, tokens = await extract_edit_entities(message.text, provider_name, api_key, entities_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
    
    if not extraction or not extraction.edits:
        await message.answer("I couldn't understand what you want to edit.")
        return
    
    responses = []
    from src.db.models import ActionLog
    
    for edit in extraction.edits:
        entity_type = (edit.entity_type or "").lower()
        
        if entity_type == "project":
            proj = None
            try:
                entity_id = int(edit.entity_name_or_id)
                proj = db.query(Project).filter(Project.id == entity_id, Project.user_id == user.id).first()
            except ValueError:
                proj = db.query(Project).filter(
                    Project.user_id == user.id,
                    func.lower(Project.title) == edit.entity_name_or_id.lower()
                ).first()
            
            if not proj:
                responses.append(f"⚠️ Project '{edit.entity_name_or_id}' not found.")
                continue
            

            if edit.action == "delete":
                prev_state = {"title": proj.title, "target_value": proj.target_value, "unit": proj.unit, "status": proj.status}
                proj.status = "archived" # Soft delete
                db.flush()
                alog = ActionLog(
                    user_id=user.id,
                    tool_name="delete_project",
                    previous_state_json=prev_state,
                    new_state_json={"id": proj.id, "status": "archived"}
                )
                db.add(alog)
                responses.append(f"🗑 Project deleted: <b>{proj.title}</b>")
                continue
            
            prev_state = {"title": proj.title, "target_value": proj.target_value, "unit": proj.unit, "parent_id": proj.parent_id}
            
            if edit.new_name:
                proj.title = edit.new_name
            if edit.new_target_value is not None:
                proj.target_value = edit.new_target_value
            if edit.new_unit:
                proj.unit = edit.new_unit
            
            if hasattr(edit, 'new_parent_project_id') and edit.new_parent_project_id is not None:
                if edit.new_parent_project_id == -1:
                    proj.parent_id = None
                else:
                    parent = db.query(Project).filter(Project.id == edit.new_parent_project_id, Project.user_id == user.id).first()
                    if parent and parent.id != proj.id:
                        proj.parent_id = parent.id
            
            db.flush()
            
            alog = ActionLog(
                user_id=user.id,
                tool_name="edit_project",
                previous_state_json={"id": proj.id, **prev_state},
                new_state_json={"id": proj.id, "title": proj.title, "target_value": proj.target_value, "unit": proj.unit, "parent_id": proj.parent_id}
            )
            db.add(alog)
            
            msg = f"✅ Project updated: <b>{proj.title}</b>"
            if proj.target_value > 0:
                msg += f" (Target: {proj.target_value} {proj.unit or 'minutes'})"
            responses.append(msg)
            
        elif entity_type == "task":
            task = None
            try:
                entity_id = int(edit.entity_name_or_id)
                task = db.query(Task).filter(Task.id == entity_id, Task.user_id == user.id).first()
            except ValueError:
                task = db.query(Task).filter(
                    Task.user_id == user.id,
                    func.lower(Task.title) == edit.entity_name_or_id.lower()
                ).first()
                
            if not task:
                responses.append(f"❌ Could not find task: {edit.entity_name_or_id}")
                continue
                
            if edit.action == "delete":
                task.status = "cancelled"
                responses.append(f"🗑 Task cancelled: <b>{task.title}</b>")
                continue
                
            if getattr(edit, 'new_status', None) == "completed":
                task.status = "completed"
                from datetime import datetime, timezone
                task.completed_at = datetime.now(timezone.utc)
                responses.append(f"✅ Task completed: <b>{task.title}</b>")
                continue
                
            if edit.new_name:
                task.title = edit.new_name
                responses.append(f"✅ Task renamed to: <b>{task.title}</b>")
        
        else:
            responses.append(f"⚠️ Unknown entity type: {entity_type}")
    
    db.commit()
    
    if responses:
        await message.answer("\n".join(responses), parse_mode="HTML")
    else:
        await message.answer("No entities were edited.")
