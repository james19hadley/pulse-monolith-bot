"""
Handlers for project actions like tracking manual progress, deleting, and archiving.

@Architecture-Map: [HND-PROJ-ACTIONS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User, Project
from src.bot.states import EntityState
from datetime import datetime, timezone
from src.bot.keyboards import get_projects_tree_keyboard, get_project_view_keyboard

# Sub-module imports for refactored logic
from .view import render_project_view
from .tasks import handle_project_tasks, handle_complete_task
from .modifications import handle_delete_project

router = Router()
from .list import cb_projects_list

@router.callback_query(F.data.startswith("ui_proj_"))
async def cb_project_action(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split("_")[2:] # ["proj", action] etc
    
    if data[0] == "archlist":
        # ...existing code...
        return

    if data[0] == "complist":
        # ...existing code...
        return

    if data[0] == "new":
        # ...existing code...
        return
        
    action_or_id = data[0]
    
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        
        if action_or_id.isdigit():
            # Project View (Refactored)
            proj_id = int(action_or_id)
            proj = db.query(Project).filter(Project.id == proj_id, Project.user_id == user.id).first()
            if not proj:
                await cb.answer("Project not found.")
                return
            
            await render_project_view(cb, db, user, proj)
            return
            
        action = action_or_id
        proj_id = int(data[1])
        proj = db.query(Project).filter(Project.id == proj_id, Project.user_id == user.id).first()
        if not proj:
            await cb.answer("Project not found.")
            return
            
        if action == "arch":
            proj.status = "archived"
            db.commit()
            await cb.answer(f"Sent {proj.title} to archive.")
            await cb_projects_list(cb, state)

        elif action == "complete":
            proj.status = "completed"
            db.commit()
            await cb.answer(f"🎉 Marked {proj.title} as completed!")
            await cb_projects_list(cb, state)

        elif action == "unarch":
            proj.status = "active"
            db.commit()
            await cb.answer(f"Restored {proj.title} from archive.")
            await cb_projects_list(cb, state)

        elif action == "uncomp":
            proj.status = "active"
            db.commit()
            await cb.answer(f"Reopened project {proj.title}.")
            await cb_projects_list(cb, state)

        elif action == "delete":
            status = await handle_delete_project(cb, db, user, proj)
            if status == "archived":
                cb = cb.model_copy(update={"data": "ui_proj_archlist"})
                await cb_project_action(cb, state)
            elif status == "completed":
                cb = cb.model_copy(update={"data": "ui_proj_complist"})
                await cb_project_action(cb, state)
            else:
                await cb_projects_list(cb, state)
            
        elif action == "addtask":
            await state.set_state(EntityState.waiting_for_task_name)
            await state.update_data(task_project_id=proj.id)
            await cb.message.edit_text(
                f"Enter the name of the new task for <b>{proj.title}</b>:\n\n(Keep it actionable, like 'Write introduction chapter')",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data=f"ui_proj_tasks_{proj.id}")]])
            )
            
        elif action == "tasks":
            await handle_project_tasks(cb, db, user, proj)

        elif action == "comptask":
            task_id = int(data[2])
            project_id = await handle_complete_task(cb, db, user, task_id)
            if project_id:
                cb = cb.model_copy(update={"data": f"ui_proj_tasks_{project_id}"})
                await cb_project_action(cb, state)
            else:
                await cb.answer("Task not found.")

        elif action == "deltask":
            from src.db.models import Task
            task_id = int(data[2])
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "deleted"
                db.commit()
                await cb.answer(f"Deleted task '{task.title}'")
                cb = cb.model_copy(update={"data": f"ui_proj_tasks_{task.project_id}"})
                await cb_project_action(cb, state)
            else:
                await cb.answer("Task not found.")

        elif action == "setfocus":
            from src.db.models import Task
            task_id = int(data[2])
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.is_focus_today = True
                db.commit()
                await cb.answer(f"Set '{task.title}' as Focus!")
                cb = cb.model_copy(update={"data": f"ui_proj_tasks_{task.project_id}"})
                await cb_project_action(cb, state)
            else:
                await cb.answer("Task not found.")

        elif action == "edit":
            # ...existing code...
            return
            
        elif action == "resetdaily":
            # ...existing code...
            return
            
        elif action == "editdaily":
            # ...existing code...
            return

        elif action == "add":
            # ...existing code...
            return


@router.callback_query(F.data.startswith("ui_proj_link_"))
async def cb_proj_link(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Feature in development! You can update DB directly for now.")
