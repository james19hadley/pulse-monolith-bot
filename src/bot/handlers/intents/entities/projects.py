"""
Logic for creating projects and habits via AI intents.
@Architecture-Map: [HND-INTENT-ENT-PROJ]
"""
from aiogram.types import Message
from sqlalchemy import func
from src.db.models import Project, ActionLog
from src.ai.router import extract_entities
from src.bot.handlers.utils import log_tokens

async def handle_create_entities(message: Message, db, user, provider_name, api_key):
    active_projs = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
    active_projects_text = "\n".join([f"[{p.id}] {p.title}" for p in active_projs])
    
    extraction, tokens = await extract_entities(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or (not extraction.projects and not extraction.habits):
        await message.answer("I could not determine the exact details for the project to create.")
        return
        
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
                
                # Log action for SMART UNDO
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
        
    db.commit()
