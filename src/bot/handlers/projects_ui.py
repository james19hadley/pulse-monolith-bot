from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.db.repo import SessionLocal
from src.db.models import User, Project, Habit
from src.bot.handlers.utils import get_or_create_user
from src.bot.texts import Buttons
from src.bot.keyboards import (
    get_entities_main_keyboard,
    get_projects_list_keyboard,
    get_habits_list_keyboard,
    get_project_view_keyboard,
    get_habit_view_keyboard
)
from src.bot.states import EntityState

router = Router()

@router.message(lambda msg: msg.text == Buttons.PROJECTS)
async def cmd_projects_menu(message: Message, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        projects = db.query(Project).filter(
            Project.user_id == user.id, 
            Project.status == "active"
        ).all()
        await message.answer(
            "<b>Your Active Projects:</b>",
            parse_mode="HTML",
            reply_markup=get_projects_list_keyboard(projects)
        )

@router.message(lambda msg: msg.text == getattr(Buttons, "HABITS", "🎯 Habits"))
async def cmd_habits_menu(message: Message, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        await message.answer(
            "<b>Your Active Habits:</b>",
            parse_mode="HTML",
            reply_markup=get_habits_list_keyboard(habits)
        )

@router.callback_query(F.data == "cancel_projects_action")
async def cb_cancel_projects_action(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Action canceled.")




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
                    text += f"{i}. {t.title}\n"
                
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_project_view_keyboard(proj.id))
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

@router.callback_query(F.data == "ui_habits_list")
async def cb_habits_list(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        await cb.message.edit_text(
            "<b>Your Active Habits:</b>",
            parse_mode="HTML",
            reply_markup=get_habits_list_keyboard(habits)
        )

@router.callback_query(F.data.startswith("ui_hab_"))
async def cb_habit_action(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split("_")[2:]
    
    if data[0] == "new":
        await state.set_state(EntityState.waiting_for_habit_name)
        await cb.message.edit_text("Enter the **name** for the new habit:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
        return
        
    action_or_id = data[0]
    
    with SessionLocal() as db:
        user = get_or_create_user(db, cb.from_user.id)
        
        if action_or_id.isdigit():
            hab_id = int(action_or_id)
            hab = db.query(Habit).filter(Habit.id == hab_id, Habit.user_id == user.id).first()
            if not hab:
                await cb.answer("Habit not found.")
                return
            
            unit = f" {hab.unit}" if hab.unit else ""
            text = f"🎯 <b>{hab.title}</b>\n\nProgress: {hab.current_value}"
            if hab.target_value:
                text += f" / {hab.target_value}{unit}"
            else:
                text += f"{unit}"
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_habit_view_keyboard(hab.id))
            return
            
        action = action_or_id
        hab_id = int(data[1])
        hab = db.query(Habit).filter(Habit.id == hab_id, Habit.user_id == user.id).first()
        if not hab:
            await cb.answer("Habit not found.")
            return
            
        if action == "arch":
            db.delete(hab)
            db.commit()
            await cb.answer(f"Deleted {hab.title}.")
            await cb_habits_list(cb, state)
            
        elif action == "edit":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_edit_habit_target)
            await cb.message.edit_text(f"Enter new target <b>value</b> for <code>{hab.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            
        elif action == "add":
            hab.current_value += 1
            db.commit()
            await cb.answer(f"Added +1 to {hab.title}!")
            
            # Refresh view
            unit = f" {hab.unit}" if hab.unit else ""
            text = f"🎯 <b>{hab.title}</b>\n\nProgress: {hab.current_value}"
            if hab.target_value:
                text += f" / {hab.target_value}{unit}"
            else:
                text += f"{unit}"
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_habit_view_keyboard(hab.id))


@router.message(EntityState.waiting_for_habit_name)
async def state_new_habit(message: Message, state: FSMContext):
    args_text = message.text
    title = args_text

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        habit = Habit(user_id=user.id, title=title, target_value=None, current_value=0)
        db.add(habit)
        db.commit()
        await message.answer(f"✅ Habit created: {habit.title}")
    await state.clear()
    
@router.message(EntityState.waiting_for_edit_habit_target)
async def state_edit_habit_target(message: Message, state: FSMContext):
    data = await state.get_data()
    hid = data.get("eid")
    
    try:
        val = int(message.text.strip())
    except:
        await message.answer("Please enter a valid integer.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        hab = db.query(Habit).filter(Habit.id == hid, Habit.user_id == user.id).first()
        if hab:
            hab.target_value = val
            db.commit()
            await message.answer(f"✅ Target for `{hab.title}` updated to {val}.", parse_mode="Markdown")
            
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

@router.callback_query(F.data == "ui_entities_menu")
async def cb_entities_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    from src.bot.keyboards import get_entities_menu_keyboard
    
    # Check if the message is the same to avoid aiogram 'Message is not modified' error
    if cb.message.text.startswith("🗂 Data & Entities Management"):
        await cb.answer()
        return
        
    try:
        await cb.message.edit_text(
            "🗂 <b>Data & Entities Management</b>\nChoose what you want to manage:",
            parse_mode="HTML",
            reply_markup=get_entities_menu_keyboard()
        )
    except Exception:
        await cb.message.delete()
        await cb.message.answer(
            "🗂 <b>Data & Entities Management</b>\nChoose what you want to manage:",
            parse_mode="HTML",
            reply_markup=get_entities_menu_keyboard()
        )
