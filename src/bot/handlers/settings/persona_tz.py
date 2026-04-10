"""
Handlers for configuring bot attitude/persona and Timezone cutoff.

@Architecture-Map: [HND-SET-PERSONA]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User
from src.bot.states import SettingsState
from src.bot.keyboards import get_persona_keyboard, get_timezone_keyboard, get_back_settings_keyboard

router = Router()

@router.message(Command("persona"))
async def cmd_persona(message: Message, command: CommandObject):
    """
    Shows or updates the current persona.
    Usage: /persona [name]
    """
    from src.core.personas import DEFAULT_PERSONAS
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        if not command.args:
            available = ", ".join(f"<code>{k}</code>" for k in DEFAULT_PERSONAS.keys())
            current = html.escape(user.persona_type)
            msg = f"<b>Current Persona:</b> <code>{current}</code>\n\n"
            msg += f"<b>Available Personas:</b>\n{available}\n\n"
            msg += "To change it, say: <code>/persona coach</code> or just tell me naturally: <i>'Change my persona to coach.'</i>"
            await message.answer(msg, parse_mode="HTML")
            return
            
        new_persona = command.args.strip().lower()
        if new_persona not in DEFAULT_PERSONAS and new_persona != "custom":
            await message.answer(f"Unknown persona. Available ones: {', '.join(DEFAULT_PERSONAS.keys())}")
            return
            
        user.persona_type = new_persona
        db.commit()
        await message.answer(f"✅ Persona successfully changed to <b>{html.escape(new_persona)}</b>.", parse_mode="HTML")


@router.callback_query(F.data.startswith("set_persona_"))
async def cq_set_persona(callback: CallbackQuery):
    persona = callback.data.replace("set_persona_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        user.persona_type = persona
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Persona set to {persona.capitalize()}!")


@router.callback_query(F.data.startswith("set_tz_"))
async def cq_set_tz(callback: CallbackQuery):
    tz = callback.data.replace("set_tz_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        user.timezone = tz
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Timezone set to {tz}!")


@router.message(SettingsState.waiting_for_tz_text)
async def process_manual_tz(message: Message, state: FSMContext):
    tz = message.text.strip()
    import zoneinfo
    try:
        # Validate that they entered a correct timezone
        zoneinfo.ZoneInfo(tz)
    except Exception:
        await message.answer("❌ Invalid timezone format. Please use standard IANA formats like 'Europe/Moscow', 'America/New_York', or 'Asia/Kolkata'. Try again:")
        return

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        user.timezone = tz
        db.commit()
        db.refresh(user)
        from src.bot.handlers.settings.general import get_control_panel_text, get_settings_keyboard
        text = get_control_panel_text(user)
        await message.answer(f"✅ Timezone set to {tz}\n\n" + text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await state.clear()


