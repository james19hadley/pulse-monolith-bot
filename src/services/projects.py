from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from src.db.repo import SessionLocal
from src.db.models import User, Project, Task, ActionLog, TimeLog
from datetime import datetime, timezone, time
import json

class ProjectService:
    @staticmethod
    def create_project(user_id: int, title: str, target_value: int) -> Project:
        """
        Creates a new project entity in the database.
        
        @Architecture-Map: [SRV-PROJ-CREATE]
        @Docs: docs/07_ARCHITECTURE_MAP.md
        """
        with SessionLocal() as db:
            proj = Project(user_id=user_id, title=title, status="active", target_value=target_value)
            db.add(proj)
            db.flush()
            
            alog = ActionLog(
                user_id=user_id, 
                tool_name="create_project", 
                previous_state_json={}, 
                new_state_json={"project_id": proj.id}
            )
            db.add(alog)
            db.commit()
            db.refresh(proj)
            return proj

    @staticmethod
    def archive_project(user_id: int, project_id: int) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                proj.status = "archived"
                db.commit()
                db.refresh(proj)
                return proj
            return None

    @staticmethod
    def unarchive_project(user_id: int, project_id: int) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                proj.status = "active"
                db.commit()
                db.refresh(proj)
                return proj
            return None

    @staticmethod
    def delete_project(user_id: int, project_id: int) -> bool:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                delete_log = ActionLog(
                    user_id=user_id,
                    tool_name="delete_project",
                    previous_state_json={"id": proj.id, "title": proj.title, "target_value": proj.target_value, "unit": proj.unit},
                    new_state_json={}
                )
                db.add(delete_log)
                db.delete(proj)
                db.commit()
                return True
            return False

    @staticmethod
    def complete_task(user_id: int, task_id: int) -> Optional[Task]:
        with SessionLocal() as db:
            task = db.query(Task).join(Project).filter(Task.id == task_id, Project.user_id == user_id).first()
            if task:
                task.status = "completed"
                db.commit()
                db.refresh(task)
                return task
            return None
            
    @staticmethod
    def set_task_focus(user_id: int, task_id: int) -> Optional[Task]:
        with SessionLocal() as db:
            task = db.query(Task).join(Project).filter(Task.id == task_id, Project.user_id == user_id).first()
            if task:
                task.is_focus_today = True
                db.commit()
                db.refresh(task)
                return task
            return None

    @staticmethod
    def set_target(user_id: int, project_id: int, value: float) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
                if is_time_based:
                    proj.target_value = int(value * 60)
                else:
                    proj.target_value = int(value)
                db.commit()
                db.refresh(proj)
                return proj
            return None

    @staticmethod
    def set_daily_target(user_id: int, project_id: int, value: float) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                if value <= 0:
                    proj.daily_target_value = None
                else:
                    proj.daily_target_value = int(value)
                db.commit()
                db.refresh(proj)
                return proj
            return None

    @staticmethod
    def reset_daily_progress(user_id: int, project_id: int) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                proj.daily_progress = 0
                db.commit()
                db.refresh(proj)
                return proj
            return None

    @staticmethod
    def add_progress(user_id: int, project_id: int, val: float) -> Optional[Project]:
        with SessionLocal() as db:
            proj = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
            if proj:
                is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
                if is_time_based:
                    log = TimeLog(user_id=user_id, project_id=proj.id, duration_minutes=int(val), description="Manual entry via UI", created_at=datetime.utcnow())
                else:
                    log = TimeLog(user_id=user_id, project_id=proj.id, duration_minutes=0, progress_amount=val, description="Manual entry via UI", created_at=datetime.utcnow())
                db.add(log)
                db.commit()
                db.refresh(proj)
                return proj
            return None

