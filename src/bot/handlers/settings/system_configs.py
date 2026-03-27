from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User
from src.bot.states import SettingsState
from src.bot.keyboards import get_catalyst_keyboard, get_interval_keyboard, get_channel_keyboard, get_pulse_menu_keyboard, get_cutoff_keyboard, get_back_settings_keyboard

router = Router()

@router.callback_query(F.data == "settings_catalyst")
async def cq_settings_catalyst(callback: CallbackQuery):
    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'catalyst_limit', 60)
    text = f"⏱️ <b>Catalyst Limit</b> (Minutes)\n\n<i>How much time should pass after the deadline before I notify you?</i>\n\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_catalyst_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("set_catalyst_"))
async def cq_set_catalyst_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_catalyst_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me a number (in minutes) for the Catalyst Limit:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_catalyst)
        return
    
    try:
        limit = int(val)
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.catalyst_limit = limit
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_data(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(SettingsState.waiting_for_catalyst)
async def process_catalyst_text(message: Message, state: FSMContext):
    try:
        limit = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.catalyst_limit = limit
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_data(message.from_user.id)
        await message.answer(f"✅ Catalyst updated.\n\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid number.")


@router.callback_query(F.data == "settings_interval")
async def cq_settings_interval(callback: CallbackQuery):
    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'interval_limit', 20)
    text = f"⏱️ <b>Ping Interval</b> (Minutes)\n\n<i>How often should I ping you to remind you about the overdue habit?</i>\n\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_interval_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("set_interval_"))
async def cq_set_interval_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_interval_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me a number (in minutes) for the Ping Interval:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_interval)
        return
    
    try:
        limit = int(val)
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.interval_limit = limit
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_data(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(SettingsState.waiting_for_interval)
async def process_interval_text(message: Message, state: FSMContext):
    try:
        limit = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.interval_limit = limit
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_data(message.from_user.id)
        await message.answer(f"✅ Interval updated.\n\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid number.")


@router.callback_query(F.data == "settings_channel")
async def cq_settings_channel(callback: CallbackQuery):
    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'target_channel_id', 'None')
    text = f"📣 <b>Target Channel</b>\n\nWhere should I post reports?\n\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_channel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("set_channel_"))
async def cq_set_channel_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_channel_", "")
    if val == "clear":
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.target_channel_id = None
            db.commit()
        text, markup = get_control_panel_data(callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        return
        
    if val == "custom":
        await callback.message.edit_text(
            "Forward a message from your channel or send the ID:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_channel)
        return


@router.message(SettingsState.waiting_for_channel)
async def process_channel_text(message: Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.target_channel_id = channel_id
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_data(message.from_user.id)
        await message.answer(f"✅ Channel updated.\n\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid ID.")


@router.callback_query(F.data == "settings_pulse")
async def cq_settings_pulse(callback: CallbackQuery):
    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        catalyst = getattr(user, 'catalyst_limit', 60)
        interval = getattr(user, 'interval_limit', 20)
    
    text = (
        "💓 <b>Pulse Intervals</b>\n\n"
        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.\n"
        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue.\n\n"
        f"<b>Current Settings:</b>\n"
        f"Catalyst: <code>{catalyst}</code> min\n"
        f"Ping: <code>{interval}</code> min"
    )
    await callback.message.edit_text(text, reply_markup=get_pulse_menu_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "settings_cutoff")
async def cq_settings_cutoff(callback: CallbackQuery):
    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'day_cutoff_time', '23:00')
    text = f"⏰ <b>Day Cutoff Time</b>\n\nAt what time should the day end for reporting purposes? (Format: HH:MM)\n\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_cutoff_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("set_cutoff_"))
async def cq_set_cutoff_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_cutoff_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me the time for your day cutoff in HH:MM format (e.g., 23:30):",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_cutoff)
        return
    
    try:
        from datetime import time
        h, m = map(int, val.split(':'))
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.day_cutoff_time = time(h, m)
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_data(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(SettingsState.waiting_for_cutoff)
async def process_cutoff_text(message: Message, state: FSMContext):
    try:
        from datetime import time
        val = message.text.strip().replace('.', ':')
        h, m = map(int, val.split(':'))
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.day_cutoff_time = time(h, m)
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_data(message.from_user.id)
        await message.answer(f"✅ Cutoff time updated.\n\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid time like '23:00'.")


