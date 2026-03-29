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

@router.callback_query(lambda c: c.data == "ui_projects_list" or c.data.startswith("ui_prjl_"))
async def cb_projects_list(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    page = 0
    toggled_ids = set()
    
    if cb.data.startswith("ui_prjl_"):
        try:
            parts = cb.data.split("_")
            page = int(parts[2])
            if len(parts) > 3 and parts[3]:
                toggled_ids = set(int(x) for x in parts[3].split(".") if x)
        except Exception:
            pass
            
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        
        all_projects = db.query(Project).filter(
            Project.user_id == user.id,
            Project.status == "active"
        ).all()
        
        title = "<b>Your Active Projects:</b>"
        
        try:
            await cb.message.edit_text(
                title,
                parse_mode="HTML",
                reply_markup=get_projects_tree_keyboard(all_projects, page=page, toggled_ids=toggled_ids)
            )
        except Exception:
            pass
        await cb.answer()


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
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            unit_str = "hours" if is_time_based else proj.unit
            await cb.message.edit_text(
                f"Enter new target <b>{unit_str}</b> for project <code>{proj.title}</code> (0 to disable target):", 
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]])
            )
            
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


@router.message(EntityState.waiting_for_project_name)
async def state_new_project(message: Message, state: FSMContext):
    args_text = message.text
    target_value = 0
    title = args_text
    
    # If the user typed a long intent-like string, tell them to use AI next time.
    if "|" in args_text:
        parts = args_text.split("|", 1)
        title = parts[0].strip()
        try:
            target_value = int(float(parts[1].strip()) * 60)
        except ValueError:
            pass

    from src.db.models import ActionLog
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = Project(user_id=user.id, title=title, status="active", target_value=target_value)
        db.add(proj)
        db.flush() # get id
        
        # LOG ACTION FOR UNDO
        alog = ActionLog(user_id=user.id, tool_name="create_project", previous_state_json={}, new_state_json={"project_id": proj.id})
        db.add(alog)
        db.commit()
        
        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                msg += f" (Target: {proj.target_value / 60:g}h)"
            else:
                msg += f" (Target: {proj.target_value:g} {proj.unit})"
                
        if "|" not in args_text and len(args_text.split()) > 3:
            msg += "\n\n<i>Next time, if you want me to understand natural language details (like 'for 30 days'), make sure you are not in the 'New Project' menu state! Just type it directly in the main chat.</i>"
            
        await message.answer(msg, parse_mode="HTML")
    await state.clear()


@router.message(EntityState.waiting_for_edit_project_target)
async def state_edit_project_target(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        val = float(message.text.strip())
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                proj.target_value = int(val * 60)
                db.commit()
                await message.answer(f"✅ Target for `{proj.title}` updated to {val:g}h.", parse_mode="Markdown")
            else:
                proj.target_value = val
                db.commit()
                await message.answer(f"✅ Target for `{proj.title}` updated to {val:g} {proj.unit}.", parse_mode="Markdown")
            
    await state.clear()


@router.message(EntityState.waiting_for_edit_project_daily_target)
async def state_edit_project_daily_target(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        val = float(message.text.strip())
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            # Note: We save daily target in the same raw unit, whether it's pages or minutes.
            if val <= 0:
                proj.daily_target_value = None
                db.commit()
                await message.answer(f"✅ Daily target disabled for `{proj.title}`.", parse_mode="Markdown")
            else:
                proj.daily_target_value = val
                db.commit()
                unit_str = "minutes" if (not proj.unit or proj.unit in ['minutes', 'hours']) else proj.unit
                await message.answer(f"✅ Daily target for `{proj.title}` updated to {val:g} {unit_str}.", parse_mode="Markdown")
            
    await state.clear()


@router.message(EntityState.waiting_for_add_project_time)
async def state_add_project_time(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("eid")
    
    try:
        val = float(message.text.strip())
    except:
        await message.answer("Please enter a valid number.")
        return
        
    with SessionLocal() as db:
        from src.db.models import TimeLog
        from datetime import datetime
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if proj:
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']
            if is_time_based:
                log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=int(val), description="Manual entry via UI", created_at=datetime.utcnow())
                msg_text = f"✅ Logged {int(val)}m to `{proj.title}`."
            else:
                log = TimeLog(user_id=user.id, project_id=proj.id, duration_minutes=0, progress_amount=val, description="Manual entry via UI", created_at=datetime.utcnow())
                msg_text = f"✅ Logged {val:g} {proj.unit} to `{proj.title}`."
                
            db.add(log)
            db.commit()
            await message.answer(msg_text, parse_mode="Markdown")
            
    await state.clear()



@router.callback_query(F.data.startswith("ui_proj_link_"))
async def cb_proj_link(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Feature in development! You can update DB directly for now.")
