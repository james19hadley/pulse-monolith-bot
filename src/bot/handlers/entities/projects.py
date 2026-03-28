from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User, Project, Habit
from src.bot.states import EntityState
from datetime import datetime, timezone
from src.bot.keyboards import get_projects_list_keyboard, get_project_view_keyboard

router = Router()

@router.callback_query(F.data == "ui_projects_list")
async def cb_projects_list(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        projects = db.query(Project).filter(
            Project.user_id == user.id, 
            Project.status == "active"
        ).all()
        await cb.message.edit_text(
            "<b>Your Active Projects:</b>",
            parse_mode="HTML",
            reply_markup=get_projects_list_keyboard(projects)
        )


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
            
            hours = proj.target_value / 60 if proj.target_value > 0 else 0
            total_hours = total_minutes / 60
            today_hours = today_minutes / 60
            
            progress_bar = ""
            if proj.target_value > 0:
                pct = min(1.0, total_minutes / proj.target_value)
                filled = int(pct * 10)
                progress_bar = "\nProgress: [" + "█" * filled + "░" * (10 - filled) + f"] {pct*100:.1f}%\n"
                
            text = f"📁 <b>{proj.title}</b>\n\nTarget Hours: {hours:g}h\nTotal Tracked: {total_hours:g}h\nToday Tracked: {today_hours:g}h\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
            if proj.unit and proj.unit != 'minutes':
                text += f"\n📈 Daily Progress: {today_progress:g} {proj.unit}"
                
            from src.db.models import Task
            pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(5).all()
            if pending_tasks:
                text += "\n\n📋 <b>Next Tasks:</b>\n"
                for i, t in enumerate(pending_tasks, 1):
                    prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
                    text += f"{i}. {prefix}{t.title}\n"
                
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id, status=proj.status))
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
            # Hack to invoke archlist
            cb = cb.model_copy(update={"data": "ui_proj_archlist"})
            await cb_project_action(cb, state)
            
        elif action == "tasks":
            from src.db.models import Task
            pending_tasks = db.query(Task).filter(Task.project_id == proj.id, Task.status == 'pending').limit(10).all()
            
            if not pending_tasks:
                await cb.answer("No pending tasks for this project.", show_alert=True)
                return
            
            kb = []
            for t in pending_tasks:
                prefix = "🎯 " if getattr(t, 'is_focus_today', False) else ""
                kb.append([InlineKeyboardButton(text=f"✅ {prefix}{t.title}", callback_data=f"ui_proj_comptask_{t.id}")])
                if not getattr(t, 'is_focus_today', False):
                    kb.append([InlineKeyboardButton(text=f"🎯 Set Focus: {t.title}", callback_data=f"ui_proj_setfocus_{t.id}")])
                    
            kb.append([InlineKeyboardButton(text="🔙 Back to Project", callback_data=f"ui_proj_{proj.id}")])
            
            await cb.message.edit_text(
                f"<b>Tasks for {proj.title}</b>\nSelect a task to complete it, or set it as today's focus:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
            )

        elif action == "comptask":
            from src.db.models import Task
            task_id = int(data[1])
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

        elif action == "setfocus":
            from src.db.models import Task
            task_id = int(data[1])
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.is_focus_today = True
                db.commit()
                await cb.answer(f"Set '{task.title}' as Focus!")
                cb = cb.model_copy(update={"data": f"ui_proj_tasks_{task.project_id}"})
                await cb_project_action(cb, state)
            else:
                await cb.answer("Task not found.")

        

        elif action == "setfocus":
            from src.db.models import Task
            task_id = int(data[1])
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
            await cb.message.edit_text(
                f"Enter new target <b>hours</b> for project <code>{proj.title}</code> (0 to disable target):", 
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )
            
        elif action == "add":
            await state.update_data(eid=proj.id)
            await state.set_state(EntityState.waiting_for_add_project_time)
            await cb.message.edit_text(f"Enter minutes to log for <code>{proj.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))


@router.message(EntityState.waiting_for_project_name)
async def state_new_project(message: Message, state: FSMContext):
    args_text = message.text
    target_value = 0
    title = args_text
    if "|" in args_text:
        parts = args_text.split("|", 1)
        title = parts[0].strip()
        try:
            target_value = int(float(parts[1].strip()) * 60)
        except ValueError:
            pass

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = Project(user_id=user.id, title=title, status="active", target_value=target_value)
        db.add(proj)
        db.commit()
        
        msg = f"✅ Project created: {proj.title}"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg)
    await state.clear()


@router.message(EntityState.waiting_for_edit_project_target)
async def state_edit_project_target(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        hours = float(message.text.strip())
        minutes = int(hours * 60)
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            proj.target_value = minutes
            db.commit()
            await message.answer(f"✅ Target for `{proj.title}` updated to {hours:g}h.", parse_mode="Markdown")
            
    await state.clear()


@router.message(EntityState.waiting_for_add_project_time)
async def state_add_project_time(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        minutes = int(message.text.strip())
    except:
        await message.answer("Please enter a valid number of minutes.")
        return
        
    with SessionLocal() as db:
        from src.db.models import TimeLog
        from datetime import datetime
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=minutes, description="Manual entry via UI", created_at=datetime.utcnow())
            db.add(log)
            db.commit()
            await message.answer(f"✅ Logged {minutes}m to `{proj.title}`.", parse_mode="Markdown")
            
    await state.clear()


