from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User, Project, Habit
from src.bot.states import EntityState
from datetime import datetime, timezone
from src.bot.keyboards import get_habits_list_keyboard, get_habit_view_keyboard


router = Router()

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
            text += f"\n🗓 Periodicity: Every {hab.periodicity_days} day(s)\n⏱ Nudge Threshold: {hab.nudge_threshold_days} day(s) missing"
            await cb.message.edit_text(text, parse_mode="HTML", reply_markup=get_habit_view_keyboard(hab.id))
            return
            
        action = action_or_id
        hab_id = int(data[1])
        hab = db.query(Habit).filter(Habit.id == hab_id, Habit.user_id == user.id).first()
        if not hab:
            await cb.answer("Habit not found.")
            return
            
        if action == "arch":
            # We must log this to Undo
            from src.db.models import ActionLog
            al = ActionLog(
                user_id=user.id,
                tool_name="delete_habit",
                previous_state_json={"habit_id": hab.id, "title": hab.title, "target_value": hab.target_value, "current_value": hab.current_value},
                new_state_json={}
            )
            db.add(al)
            db.delete(hab)
            db.commit()
            await cb.answer(f"Deleted {hab.title}.")
            await cb_habits_list(cb, state)
            
        elif action == "edit":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_edit_habit_target)
            await cb.message.edit_text(f"Enter new target <b>value</b> for <code>{hab.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            
        elif action == "period":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_habit_periodicity)
            await cb.message.edit_text(f"Enter new periodicity in <b>days</b> (e.g. 1 for daily) for <code>{hab.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            return

        elif action == "nudge":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_habit_nudge)
            await cb.message.edit_text(f"Enter new nudge threshold in <b>days</b> for <code>{hab.title}</code> (0 to disable nudges):", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            return

        elif action == "period":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_habit_periodicity)
            await cb.message.edit_text(f"Enter new periodicity in <b>days</b> (e.g. 1 for daily) for <code>{hab.title}</code>:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            return

        elif action == "nudge":
            await state.update_data(eid=hab.id)
            await state.set_state(EntityState.waiting_for_habit_nudge)
            await cb.message.edit_text(f"Enter new nudge threshold in <b>days</b> for <code>{hab.title}</code> (0 to disable nudges):", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_projects_action")]]))
            return

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
            text += f"\n🗓 Periodicity: Every {hab.periodicity_days} day(s)\n⏱ Nudge Threshold: {hab.nudge_threshold_days} day(s) missing"
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


@router.message(EntityState.waiting_for_habit_periodicity)
async def state_edit_habit_periodicity(message: Message, state: FSMContext):
    data = await state.get_data()
    hid = data.get("eid")
    
    try:
        val = int(message.text.strip())
        if val < 1:
            raise ValueError
    except:
        await message.answer("Please enter a valid positive integer (e.g., 1 for daily).")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        hab = db.query(Habit).filter(Habit.id == hid, Habit.user_id == user.id).first()
        if hab:
            hab.periodicity_days = val
            db.commit()
            
            unit = f" {hab.unit}" if hab.unit else ""
            text = f"🎯 <b>{hab.title}</b>\\n\\nProgress: {hab.current_value}"
            if hab.target_value:
                text += f" / {hab.target_value}{unit}"
            else:
                text += f"{unit}"
            text += f"\\n🗓 Periodicity: Every {hab.periodicity_days} day(s)\\n⏱ Nudge Threshold: {hab.nudge_threshold_days} day(s) missing"
            
            await message.answer(f"✅ Periodicity for {hab.title} updated!", parse_mode="HTML")
            await message.answer(text, parse_mode="HTML", reply_markup=get_habit_view_keyboard(hab.id))
    await state.clear()


@router.message(EntityState.waiting_for_habit_nudge)
async def state_edit_habit_nudge(message: Message, state: FSMContext):
    data = await state.get_data()
    hid = data.get("eid")
    
    try:
        val = int(message.text.strip())
        if val < 0:
            raise ValueError
    except:
        await message.answer("Please enter a valid integer (0 or greater).")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        hab = db.query(Habit).filter(Habit.id == hid, Habit.user_id == user.id).first()
        if hab:
            hab.nudge_threshold_days = val
            db.commit()
            
            unit = f" {hab.unit}" if hab.unit else ""
            text = f"🎯 <b>{hab.title}</b>\\n\\nProgress: {hab.current_value}"
            if hab.target_value:
                text += f" / {hab.target_value}{unit}"
            else:
                text += f"{unit}"
            text += f"\\n🗓 Periodicity: Every {hab.periodicity_days} day(s)\\n⏱ Nudge Threshold: {hab.nudge_threshold_days} day(s) missing"
            
            await message.answer(f"✅ Nudge threshold for {hab.title} updated!", parse_mode="HTML")
            await message.answer(text, parse_mode="HTML", reply_markup=get_habit_view_keyboard(hab.id))
    await state.clear()


