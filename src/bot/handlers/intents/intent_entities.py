from aiogram.types import Message
from src.ai.router import extract_entities, extract_inbox, extract_add_tasks
from src.bot.handlers.utils import log_tokens
async def _handle_create_entities(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Habit
    extraction, tokens = extract_entities(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or (not extraction.projects and not extraction.habits):
        await message.answer("I could not determine the exact details for the project or habit to create.")
        return
        
    responses = []
    
    from sqlalchemy import func
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    for p in extraction.projects:
        existing = db.query(Project).filter(Project.user_id == user.id, func.lower(Project.title) == p.title.lower()).first()
        if existing:
            if existing.status == "archived":
                existing.status = "active"
                existing.target_value = getattr(p, 'target_value', 0)
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
                    msg += f" (Target: {existing.target_value})"
                if hasattr(existing, 'unit') and existing.unit:
                    msg += f" {existing.unit}"
                await message.answer(msg, parse_mode="HTML")
            else:
                await message.answer(f"⚠️ Project already exists: <b>{existing.title}</b>", parse_mode="HTML")
            continue
            
        proj = Project(user_id=user.id, title=p.title, status="active", target_value=getattr(p, 'target_value', 0))
        if hasattr(p, 'unit') and p.unit:
            proj.unit = p.unit
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
        await message.answer(msg, parse_mode="HTML")
        
    for h in extraction.habits:
        existing = db.query(Habit).filter(Habit.user_id == user.id, func.lower(Habit.title) == h.title.lower()).first()
        if existing:
            await message.answer(f"⚠️ Habit already exists: <b>{existing.title}</b>", parse_mode="HTML")
            continue

        unit = getattr(h, "unit", "times")
        habit = Habit(user_id=user.id, title=h.title, target_value=h.target_value, unit=unit, type="counter")
        db.add(habit)
        db.flush()
        
        # Log action for SMART UNDO
        from src.db.models import ActionLog
        import json
        alog = ActionLog(user_id=user.id, tool_name="create_habit", previous_state_json={}, new_state_json={"habit_id": habit.id})
        db.add(alog)
        
        await message.answer(f"✅ Habit created: <b>{habit.title}</b>", parse_mode="HTML")
        
    db.commit()


async def _handle_add_inbox(message: Message, db, user, provider_name, api_key):
    from src.db.models import Inbox
    from src.bot.handlers.utils import log_tokens
    
    extraction, tokens = extract_inbox, extract_add_tasks(message.text, provider_name, api_key)
    
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
    
    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_projects_text = "User has no active projects yet."
    else:
        active_projects_text = "User's active projects:\n" + "\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    extraction, tokens = extract_add_tasks(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not extraction.tasks:
        await message.answer("I could not verify the exact tasks to add.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    count = 0
    msg_lines = []
    
    for t in extraction.tasks:
        project_id = t.project_id
        if project_id is None and t.unmatched_project_name:
            # We skip creating standalone tasks if they explicitly meant a project but we missed it. 
            # Or we could prompt a keyboard. Let's just create it as standalone and notify.
            pass
            
        task = Task(
            user_id=user.id,
            project_id=project_id,
            title=t.title,
            status='pending'
        )
        db.add(task)
        count += 1
        
        proj_name = "(Standalone)"
        if project_id:
            proj = next((p for p in projects if p.id == project_id), None)
            if proj:
                proj_name = proj.title
            
        msg_lines.append(f"• {t.title} 📂 <i>{proj_name}</i>")
        
    db.commit()
    
    nl = '\n'
    await message.answer(f"✅ <b>Added {count} task(s):</b>\n{nl.join(msg_lines)}", parse_mode="HTML")



async def _handle_edit_entities(message: Message, db, user, provider_name, api_key):
    """Handle entity renaming and property modification"""
    from src.db.models import Project, Habit
    from src.ai.router import extract_edit_entities
    from sqlalchemy import func
    
    # Fetch all user entities for context
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    
    entities_list = []
    for p in projects:
        entities_list.append(f"Project: {p.title} (ID: {p.id}, Target: {p.target_value} {p.unit or 'minutes'})")
    for h in habits:
        entities_list.append(f"Habit: {h.title} (ID: {h.id}, Target: {h.target_value} {h.unit or 'times'})")
    
    if not entities_list:
        await message.answer("You have no projects or habits to edit yet.")
        return
    
    entities_text = "Your entities:\n" + "\n".join(entities_list)
    
    # Extract edit requests
    extraction, tokens = extract_edit_entities(message.text, provider_name, api_key, entities_text)
    
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
            
            prev_state = {"title": proj.title, "target_value": proj.target_value, "unit": proj.unit}
            
            if edit.new_name:
                proj.title = edit.new_name
            if edit.new_target_value is not None:
                proj.target_value = edit.new_target_value
            if edit.new_unit:
                proj.unit = edit.new_unit
            
            db.flush()
            
            alog = ActionLog(
                user_id=user.id,
                tool_name="edit_project",
                previous_state_json=prev_state,
                new_state_json={"id": proj.id, "title": proj.title, "target_value": proj.target_value, "unit": proj.unit}
            )
            db.add(alog)
            
            msg = f"✅ Project updated: <b>{proj.title}</b>"
            if proj.target_value > 0:
                msg += f" (Target: {proj.target_value} {proj.unit or 'minutes'})"
            responses.append(msg)
        
        elif entity_type == "habit":
            habit = None
            try:
                entity_id = int(edit.entity_name_or_id)
                habit = db.query(Habit).filter(Habit.id == entity_id, Habit.user_id == user.id).first()
            except ValueError:
                habit = db.query(Habit).filter(
                    Habit.user_id == user.id,
                    func.lower(Habit.title) == edit.entity_name_or_id.lower()
                ).first()
            
            if not habit:
                responses.append(f"⚠️ Habit '{edit.entity_name_or_id}' not found.")
                continue
            
            prev_state = {"title": habit.title, "target_value": habit.target_value, "unit": habit.unit}
            
            if edit.new_name:
                habit.title = edit.new_name
            if edit.new_target_value is not None:
                habit.target_value = edit.new_target_value
            if edit.new_unit:
                habit.unit = edit.new_unit
            
            db.flush()
            
            alog = ActionLog(
                user_id=user.id,
                tool_name="edit_habit",
                previous_state_json=prev_state,
                new_state_json={"id": habit.id, "title": habit.title, "target_value": habit.target_value, "unit": habit.unit}
            )
            db.add(alog)
            
            msg = f"✅ Habit updated: <b>{habit.title}</b>"
            if habit.target_value > 1:
                msg += f" (Target: {habit.target_value} {habit.unit or 'times'})"
            responses.append(msg)
        else:
            responses.append(f"⚠️ Unknown entity type: {entity_type}")
    
    db.commit()
    
    if responses:
        await message.answer("\n".join(responses), parse_mode="HTML")
    else:
        await message.answer("No entities were edited.")
