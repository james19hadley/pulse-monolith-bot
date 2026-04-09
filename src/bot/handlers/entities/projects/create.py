"""
FSM telegram handler that asks the user for the project name and calls the [SRV-PROJ-CREATE] service.

@Architecture-Map: [HND-PROJ-CREATE]
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

router = Router()
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



@router.message(EntityState.waiting_for_task_name)
async def state_new_task(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("task_project_id")
    if not pid:
        await message.answer("Error: Lost project context.")
        await state.clear()
        return
        
    task_name = message.text.strip()
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        proj = db.query(Project).filter(Project.id == pid, Project.user_id == user.id).first()
        if not proj:
            await message.answer("Project not found.")
            await state.clear()
            return

        from src.db.models import Task
        new_task = Task(project_id=proj.id, title=task_name, status="pending")
        db.add(new_task)
        db.commit()
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Tasks", callback_data=f"ui_proj_tasks_{proj.id}")]
        ])
        
        await message.answer(f"✅ Created task: <b>{task_name}</b> for {proj.title}", parse_mode="HTML", reply_markup=kb)
        
    await state.clear()
