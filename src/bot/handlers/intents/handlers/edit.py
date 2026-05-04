"""
Logic for editing and deleting projects/tasks via AI intents.
@Architecture-Map: [HND-INTENT-ENT-EDIT]
"""
from aiogram.types import Message
from sqlalchemy import func
from src.db.models import Project, Task, ActionLog
from src.ai.router import extract_edit_entities
from src.bot.handlers.utils import log_tokens

async def handle_edit_entities(message: Message, db, user, provider_name, api_key):
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
