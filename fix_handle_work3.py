import re

with open('src/bot/handlers/ai_router.py', 'r') as f:
    text = f.read()

# Replace undo:work with undo_work_
text = text.replace("undo:work:{log.id}", "undo_work_{log.id}")
text = text.replace("create_project:{title[:15]}", "create_project_{title[:15]}")

new_callbacks = """
@router.callback_query(F.data.startswith("create_project_"))
async def cq_create_project(callback: aiogram.types.CallbackQuery):
    title = callback.data.replace("create_project_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        from src.db.models import Project
        project = Project(user_id=user.id, title=title)
        db.add(project)
        db.commit()
        db.refresh(project)
        await callback.message.edit_text(f"✅ Project created: <b>{project.title}</b>! Try logging time to it again.", parse_mode="HTML")

@router.callback_query(F.data.startswith("undo_work_"))
async def cq_undo_work(callback: aiogram.types.CallbackQuery):
    log_id_str = callback.data.replace("undo_work_", "")
    log_id = int(log_id_str)
    
    with SessionLocal() as db:
        from src.db.models import TimeLog, Project
        user = get_or_create_user(db, callback.from_user.id)
        log = db.query(TimeLog).filter_by(id=log_id, user_id=user.id).first()
        if log:
            project = db.query(Project).filter_by(id=log.project_id).first()
            if project:
                project.total_minutes_spent -= log.duration_minutes
                if project.total_minutes_spent < 0:
                    project.total_minutes_spent = 0
            
            db.delete(log)
            db.commit()
            await callback.message.edit_text(f"↩️ Undid {log.duration_minutes}m log.", parse_mode="HTML")
        else:
            await callback.message.edit_text("❌ Could not undo (log might not exist or already undone).", parse_mode="HTML")
"""

if "@router.callback_query(F.data.startswith(\"create_project_\"))" not in text:
    text += new_callbacks

with open('src/bot/handlers/ai_router.py', 'w') as f:
    f.write(text)
