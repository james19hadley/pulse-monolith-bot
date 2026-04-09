"""
Processing NLP session commands (Start, Stop, Pause).

@Architecture-Map: [HND-INTENT-SESS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import Message
from src.db.models import TokenUsage, Project, TimeLog, Session
from src.bot.texts import Prompts
from src.bot.handlers.utils import get_or_create_user
from src.ai.router import extract_log_work, extract_session_control
from datetime import datetime, timezone

async def _handle_session_control(message: Message, db, user, provider_name, api_key):
    from src.ai.router import extract_session_control
    from src.db.models import Session
    from datetime import datetime
    

    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_projects_text = "User has no active projects yet."
    else:
        active_projects_text = "User's active projects:\n" + "\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    params, tokens = extract_session_control(message.text, provider_name, api_key, active_projects_text)
    if tokens:
        from src.bot.handlers.utils import log_tokens
        log_tokens(db, user.id, tokens)
        
    if not params:

        await message.answer("Я не смог разобрать команду для управления сессией. 😬")
        return
        
    action = params.action.upper()
    active_session_id = user.active_session_id
    
    if action == "START":
        if active_session_id:
            await message.answer("🚨 У тебя уже есть активная сессия! Сначала заверши её.")
            return
            
        if params.project_id:
            project = db.query(Project).filter_by(id=params.project_id, user_id=user.id).first()
            if project:
                new_session = Session(user_id=user.id, project_id=project.id)
            else:
                new_session = Session(user_id=user.id)
        else:
            new_session = Session(user_id=user.id)
            
        db.add(new_session)
        db.commit()
        
        user.active_session_id = new_session.id
        db.commit()
        
        # Determine if we started contextually with a project
        if params.project_id:
            project = db.query(Project).filter_by(id=params.project_id, user_id=user.id).first()
            if project:
                await message.answer(f"🔥 Сессия начата для: <b>{project.title}</b>. Не отвлекайся. Когда закончишь, просто скажи.", parse_mode="HTML")
            else:
                await message.answer("🔥 Сессия начата. (Не смог найти указанный проект). Не отвлекайся. Когда закончишь, просто скажи.")
        else:
            await message.answer("🔥 Сессия начата. Не отвлекайся. Когда закончишь, просто скажи.")
        
    elif action == "REST":
        if not active_session_id:
            await message.answer("Нет активной сессии для перерыва.")
            return
            
        session = db.query(Session).filter(Session.id == active_session_id).first()
        if session:
            session.status = "rest"
            session.rest_start_time = datetime.utcnow()
            session.save_state_context = params.context
            db.commit()
            
            # Basic dopamine receipt
            total_elapsed = datetime.utcnow() - session.start_time
            minutes = total_elapsed.total_seconds() / 60
            hrs = int(minutes // 60)
            mins = int(minutes % 60)
            worked_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"
            
            ctx_msg = f"\nSave-State Context: «{params.context}»" if params.context else ""
            await message.answer(f"⏸️ **Rest Mode**. Acknowledged.\nTime so far: {worked_str}.\nGo breathe.{ctx_msg}", parse_mode="Markdown")
            
    elif action == "RESUME":
        if not active_session_id:
            await message.answer("Нет активной сессии для продолжения.")
            return
            
        session = db.query(Session).filter(Session.id == active_session_id).first()
        if session:
            session.status = "active"
            session.rest_start_time = None
            session.save_state_context = None
            db.commit()
            await message.answer("▶️ Сессия продолжена. Погнали дальше!")
            
    elif action == "END":
        if not active_session_id:
            await message.answer("Ты сейчас не в процессе работы (нет активной сессии).")
            return
            
        session = db.query(Session).filter(Session.id == active_session_id).first()
        if session:
            session.end_time = datetime.utcnow()
            session.status = "pending_split"
            
            project_title = "Неизвестный проект"
            if session.project_id:
                proj = db.query(Project).filter_by(id=session.project_id).first()
                if proj:
                    project_title = proj.title

            total_elapsed = session.end_time - session.start_time
            minutes = total_elapsed.total_seconds() / 60
            hrs = int(minutes // 60)
            mins = int(minutes % 60)
            
            db.commit()
            await message.answer(f"🛑 **Finished**. Total time elapsed: {hrs}h {mins}m.\n\n"
                                 f"Как разделим чек? Сколько из этого была реальная работа над **{project_title}**, а сколько списать на рутину (Project 0) (отвлекся)?",
                                 parse_mode="Markdown")


