from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User, Project
from src.bot.states import EntityState
from datetime import datetime, timezone
from src.bot.texts import Buttons
from src.bot.keyboards import get_entities_main_keyboard, get_projects_list_keyboard, get_habits_list_keyboard

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
        habits = db.query().filter(.user_id == user.id).all()
        await message.answer(
            "<b>Your Active Habits:</b>",
            parse_mode="HTML",
            reply_markup=get_habits_list_keyboard(habits)
        )


@router.callback_query(F.data == "ui_entities_menu")
async def cb_entities_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    from src.bot.keyboards import get_entities_main_keyboard
    
    # Check if the message is the same to avoid aiogram 'Message is not modified' error
    if cb.message.text.startswith("🗂 Data & Entities Management"):
        await cb.answer()
        return
        
    try:
        await cb.message.edit_text(
            "🗂 <b>Data & Entities Management</b>\nChoose what you want to manage:",
            parse_mode="HTML",
            reply_markup=get_entities_main_keyboard()
        )
    except Exception:
        await cb.message.delete()
        await cb.message.answer(
            "🗂 <b>Data & Entities Management</b>\nChoose what you want to manage:",
            parse_mode="HTML",
            reply_markup=get_entities_main_keyboard()
        )


@router.callback_query(F.data == "cancel_projects_action")
async def cb_cancel_projects_action(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Action canceled.")


