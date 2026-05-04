"""
Project modification logic (archive, complete, delete).
@Architecture-Map: [HND-PROJ-MOD]
"""
import json
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session
from src.db.models import Project, ActionLog, TimeLog, Task, Session as AppSession

async def handle_delete_project(cb: CallbackQuery, db: Session, user, proj: Project):
    status = proj.status
    delete_log = ActionLog(
        user_id=user.id,
        tool_name="delete_project",
        previous_state_json=json.dumps({
            "id": proj.id,
            "title": proj.title,
            "target_value": proj.target_value,
            "unit": proj.unit
        }),
        new_state_json={}
    )
    db.add(delete_log)
    
    # Handle foreign key constraints explicitly
    db.query(TimeLog).filter(TimeLog.project_id == proj.id).update({TimeLog.project_id: None})
    db.query(Task).filter(Task.project_id == proj.id).update({Task.project_id: None})
    db.query(AppSession).filter(AppSession.project_id == proj.id).update({AppSession.project_id: None})
    db.query(Project).filter(Project.parent_id == proj.id).update({Project.parent_id: None})
    
    db.delete(proj)
    db.commit()
    await cb.answer(f"Deleted {proj.title}.")
    return status
