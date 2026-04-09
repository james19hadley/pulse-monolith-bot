"""
Handlers for project actions like tracking manual progress, deleting, and archiving.

@Architecture-Map: [HND-PROJ-ACTIONS]
@Docs: docs/07_ARCHITECTURE_MAP.md
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

router = Router()
from .list import cb_projects_list

@router.callback_query(F.data.startswith("ui_proj_"))
async def cb_project_action(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split("_")[2:] # ["proj", action] etc
    
    if data[0] == "archlist":
        await state.clear()
        with SessionLocal() as db:
            user = get_or_create_user(db, cb.from_user.id)
            projects = db.query(Project).filter(
                Project.user_id == user.id, 
                Project.status == "archived"
            ).all()
            kb = []
            for p in projects:
                kb.append([InlineKeyboardButton(text=f"📦 {p.title}", callback_data=f"ui_proj_{p.id}")])
            kb.append([InlineKeyboardButton(text="🔙 Back to Active", callback_data="ui_projects_list")])
            await cb.message.edit_text(
                "<b>Archived Projects:</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
            )
        return

    if data[0] == "new":
        await state.set_state(EntityState.waiting_for_project_name)
        await cb.message.edit_text("Enter the **name** and **target hours** for the new project (e.g. `My Project | 50`).", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
        return
        
    action_or_id = data[0]
    
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        
        if action_or_id.isdigit():
            # Project View
            proj_id = int(action_or_id)
            proj = db.query(Project).filter(Project.id == proj_id, Project.user_id == user.id).first()
            if not proj:
                await cb.answer("Project not found.")
                return
            
            from datetime import datetime, time
            from src.db.models import TimeLog
            today_start = datetime.combine(datetime.utcnow().date(), time.min)
            logs = db.query(TimeLog).filter(TimeLog.project_id == proj.id).all()
            total_minutes = sum([l.duration_minutes for l in logs])
            today_minutes = sum([l.duration_minutes for l in logs if l.created_at >= today_start])
            
            now_dt = datetime.now(timezone.utc)
            last_active_str = "Never"
            if logs:
                last_log_dt = max(l.created_at for l in logs).replace(tzinfo=timezone.utc)
                diff = now_dt - last_log_dt
                if diff.total_seconds() < 3600:
                    last_active_str = f"{int(diff.total_seconds() // 60)} mins ago"
                elif diff.total_seconds() < 86400:
                    last_active_str = f"{int(diff.total_seconds() // 3600)} hours ago"
                else:
                    last_active_str = f"{diff.days} days ago"

            today_progress = sum([l.progress_amount or 0 for l in logs if l.created_at >= today_start and l.progress_amount])
            total_progress = sum([l.progress_amount or 0 for l in logs if l.progress_amount])

            total_hours = total_minutes / 60
            today_hours = today_minutes / 60
            
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']

            progress_bar = ""
            if proj.target_value > 0:
                if is_time_based:
                    pct = min(1.0, (total_minutes / proj.target_value) if proj.target_value else 0)
                else:
                    pct = min(1.0, (total_progress / proj.target_value) if proj.target_value else 0)
                filled = int(pct * 10)
                progress_bar = "\nProgress: [" + "█" * filled + "░" * (10 - filled) + f"] {pct*100:.1f}%\n"
                
            if is_time_based:
                hours = proj.target_value / 60 if proj.target_value > 0 else 0
                text = f"📁 <b>{proj.title}</b>\n\nTarget Hours: {hours:g}h\nTotal Tracked: {total_hours:g}h\nToday Tracked: {today_hours:g}h\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
            else:
                text = f"📁 <b>{proj.title}</b>\n\nTarget: {proj.target_value:g} {proj.unit}\nTotal Progress: {total_progress:g} {proj.unit}\nToday Progress: {today_progress:g} {proj.unit}\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"

            if getattr(proj, 'daily_target_value', None) is not None:
                streak = getattr(proj, 'current_streak', 0)
                daily_prog = getattr(proj, 'daily_progress', 0)
                emoji = "🔥" if streak > 0 else "🎯"
                text += f"\n{emoji} Daily Target: {daily_prog:g} / {proj.daily_target_value:g} {proj.unit or 'min'}"
                if streak > 0:
                    text += f" (Streak: {streak} days)"

            from src.db.models import Task
            pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(5).all()
            if pending_tasks:
                text += "\n\n📋 <b>Next Tasks:</b>\n"
                for i, t in enumerate(pending_tasks, 1):
                    prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
                    text += f"{i}. {prefix}{t.title}\n"
                
            sub_count = db.query(Project).filter(Project.parent_id == proj.id, Project.status != "deleted").count()
            parent_id = proj.parent_id
            if parent_id:
                parent = db.query(Project).filter(Project.id == parent_id).first()
                if parent:
                    text = text.replace(f"📁 <b>{proj.title}</b>", f"📂 <b>{parent.title} ➡ {proj.title}</b>")
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id, status=proj.status, sub_count=sub_count, parent_id=parent_id))
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

        elif action == "unarch":
            proj.status = "active"
            db.commit()
            await cb.answer(f"Restored {proj.title} from archive.")
            await cb_projects_list(cb, state)

        elif action == "delete":
            # Real delete
            status = proj.status
            from src.db.models import ActionLog
            import json
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
            db.delete(proj)
            db.commit()
            await cb.answer(f"Deleted {proj.title}.")
            if status == "archived":
                cb = cb.model_copy(update={"data": "ui_proj_archlist"})
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
            from src.db.models import Task
            pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(10).all()
            
            kb = []
            kb.append([InlineKeyboardButton(text="➕ Add Task", callback_data=f"ui_proj_addtask_{proj.id}")])
            
            for t in pending_tasks:
                prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
                row = [
                    InlineKeyboardButton(text=f"✅ {prefix}{t.title}", callback_data=f"ui_proj_comptask_{proj.id}_{t.id}"),
                    InlineKeyboardButton(text="🗑", callback_data=f"ui_proj_deltask_{proj.id}_{t.id}")
                ]
                kb.append(row)
                if not getattr(t, 'is_focus_today', False):
                    kb.append([InlineKeyboardButton(text=f"🎯 Set Focus: {t.title}", callback_data=f"ui_proj_setfocus_{proj.id}_{t.id}")])
                    
            kb.append([InlineKeyboardButton(text="🔙 Back to Project", callback_data=f"ui_proj_{proj.id}")])
            
            msg_text = f"<b>Tasks for {proj.title}</b>"
            if pending_tasks:
                msg_text += "\nSelect a task to complete it, or set it as today's focus:"
            else:
                msg_text += "\nNo pending tasks. Add one to clear your mind!"
                
            await cb.message.edit_text(
                msg_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
            )

        elif action == "comptask":
            from src.db.models import Task
            task_id = int(data[2])
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "completed"
                db.commit()
                
                # Check for gentle AI follow up
                if getattr(task, 'is_focus_today', False) and user.api_key_encrypted:
                    from src.core.security import decrypt_key
                    from src.ai.providers import GoogleProvider
                    import asyncio
                    try:
                        api_key = decrypt_key(user.api_key_encrypted)
                        ai = GoogleProvider(api_key=api_key)
                        prompt = f"The user just finished their 'Focus of the Day' task: '{task.title}'. Be a gentle productivity sherpa. Congratulate them warmly but briefly, and ask gently if they'd like to tackle one more, or call it a day to avoid burnout."
                        
                        async def send_followup(text, chat_id):
                            from src.main import bot
                            if bot:
                                await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
                        
                        followup_text = await ai.generate_text(prompt)
                        asyncio.create_task(send_followup(followup_text, cb.from_user.id))
                        
                    except Exception as e:
                        pass

                await cb.answer(f"Task '{task.title}' completed!")
                # Go back to task list or project
                # Re-invoke tasks via hack
                cb = cb.model_copy(update={"data": f"ui_proj_tasks_{task.project_id}"})
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
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_edit_project_target)
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            unit_str = "hours" if is_time_based else proj.unit
            await cb.message.edit_text(
                f"Enter new target <b>{unit_str}</b> for project <code>{proj.title}</code> (0 to disable target):", 
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )
            
        elif action == "resetdaily":
            proj.daily_progress = 0
            db.commit()
            await cb.answer("🧹 Daily Progress Reset to 0")
            # Return to project view
            cb = cb.model_copy(update={"data": f"ui_proj_{proj.id}"})
            await cb_project_action(cb, state)
            
        elif action == "editdaily":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_edit_project_daily_target)
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            unit_str = "minutes" if is_time_based else proj.unit
            await cb.message.edit_text(
                f"Enter new **DAILY** target <b>{unit_str}</b> for project <code>{proj.title}</code> (0 to disable daily target):",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )

        elif action == "add":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_add_project_time)
            unit_str = proj.unit if proj.unit and proj.unit not in ['minutes', 'hours'] else 'minutes'
            await cb.message.edit_text(f"Enter <b>{unit_str}</b> to log for <code>{proj.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))


@router.callback_query(F.data.startswith("ui_proj_link_"))
async def cb_proj_link(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Feature in development! You can update DB directly for now.")
