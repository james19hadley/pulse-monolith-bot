"""
General settings menu handlers.

@Architecture-Map: [HND-SET-GENERAL]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User
from src.bot.keyboards import get_settings_keyboard, get_api_keys_manage_keyboard, get_back_settings_keyboard, get_reports_keyboard, get_timezone_keyboard, get_persona_keyboard

router = Router()

def get_control_panel_data(user_id: int):
    with SessionLocal() as db:
        user = get_or_create_user(db, user_id)
        text = get_control_panel_text(user)
    return text, get_settings_keyboard()


def get_control_panel_text(user) -> str:
    provider = user.llm_provider or "None"
    persona = user.persona_type or "monolith"
    tz = user.timezone or "UTC"
    cutoff = getattr(user, 'day_cutoff_time', '23:00')
    channel = getattr(user, 'target_channel_id', 'None')
    catalyst = getattr(user, 'catalyst_threshold_minutes', 60)
    interval = getattr(user, 'catalyst_interval_minutes', 20)

    config = user.report_config
    if isinstance(config, str):
        import json
        try:
            config = json.loads(config)
        except:
            config = None
    if not config:
        config = {"destination": "dm"}
        
    reports = config.get('destination', 'dm')

    return (
        f"⚙️ <b>Pulse Monolith Control Panel</b>\n\n"
        f"<code>catalyst</code>: {catalyst} <i>(Catalyst Ping Threshold)</i>\n"
        f"<code>interval</code>: {interval} <i>(Catalyst Repeat Interval)</i>\n"
        f"<code>channel</code>: {channel} <i>(Target Channel ID)</i>\n"
        f"<code>report</code>: {reports} <i>(Dest: dm / channel / none)</i>\n"
        f"<code>cutoff</code>: {cutoff} <i>(Day Cutoff Time)</i>\n"
        f"<code>timezone</code>: {tz} <i>(Timezone)</i>\n"
        f"<code>persona</code>: {persona} <i>(Bot Persona)</i>\n"
        f"<code>provider</code>: {provider} <i>(Active LLM Provider)</i>\n\n"
        f"To change settings, you can simply text me (e.g. <code>\'set timezone to Europe/London\'</code>).\n\n"
        f"<i>Select an option below for quick actions:</i>"
    )


@router.message(Command("settings"))
@router.message(lambda msg: msg.text == "⚙️ Settings")
async def cmd_general_settings(message: Message):
    if not message.from_user:
        return
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        provider = user.llm_provider or "None"
        persona = user.persona_type or "monolith"
        tz = user.timezone or "UTC"
        cutoff = getattr(user, 'day_cutoff_time', '23:00')
        channel = getattr(user, 'target_channel_id', 'None')
        catalyst = getattr(user, 'catalyst_threshold_minutes', 60)
        interval = getattr(user, 'catalyst_interval_minutes', 20)

        # Checking report block config
        config = user.report_config
        if isinstance(config, str):
            import json
            try:
                config = json.loads(config)
            except:
                config = None
        if not config:
            config = {"destination": "dm"}
            
        reports = config.get('destination', 'dm')

        text = "⚙️ <b>Pulse Monolith Control Panel</b>\n\n"
        text += f"<code>catalyst</code>: {catalyst} <i>(Catalyst Ping Threshold)</i>\n"
        text += f"<code>interval</code>: {interval} <i>(Catalyst Repeat Interval)</i>\n"
        text += f"<code>channel</code>: {channel} <i>(Target Channel ID)</i>\n"
        text += f"<code>report</code>: {reports} <i>(Dest: dm / channel / none)</i>\n"
        text += f"<code>cutoff</code>: {cutoff} <i>(Day Cutoff Time)</i>\n"
        text += f"<code>timezone</code>: {tz} <i>(Timezone)</i>\n"
        text += f"<code>persona</code>: {persona} <i>(Bot Persona)</i>\n"
        text += f"<code>provider</code>: {provider} <i>(Active LLM Provider)</i>\n\n"
        text += "To change settings, you can simply text me (e.g. <code>'set timezone to Europe/London'</code> or <code>'disable reports'</code>).\n\n"
        text += "<i>Select an option below for quick actions:</i>"

        await message.answer(text, parse_mode="HTML", reply_markup=get_settings_keyboard())


@router.callback_query(F.data.in_({"settings_keys", "settings_add_key", "settings_persona", "settings_timezone", "settings_reports", "settings_back", "settings_main", "settings_close"}))
async def cq_settings_stubs(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "settings_keys":
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                keys = user.api_keys or {}
                if not keys:
                    msg = "<b>API Keys</b>\n\nYou have no keys configured yet."
                else:
                    msg = "<b>API Keys</b>\n\nYou have configured:\n"
                    for k in keys.keys():
                        msg += f"✅ <code>{k}</code>\n"
            await callback.message.edit_text(
                msg,
                reply_markup=get_api_keys_manage_keyboard(keys, user.llm_provider),
                parse_mode="HTML"
            )
            await callback.answer()
        elif callback.data == "settings_add_key":
            await callback.message.edit_text(
                "Select your AI Provider to securely configure your API key:",
                reply_markup=get_providers_keyboard()
            )
            await state.set_state(AddKeyState.waiting_for_provider)
            await callback.answer()
        elif callback.data == "settings_persona":
            await callback.message.edit_text("<b>Choose a Persona:</b>\n\nEach persona has a different style.", parse_mode="HTML", reply_markup=get_persona_keyboard())
            await callback.answer()
        elif callback.data == "settings_memory":
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                memory_dict = user.user_memory or {}
                
                if not memory_dict:
                    msg = "🧠 <b>Memory Space</b>\n\nI don't have any specific personal facts or preferences stored yet.\n\n<i>To add something, just tell me: 'Remember that I prefer morning workouts'.</i>"
                else:
                    msg = "🧠 <b>Memory Space</b>\n\nHere are the personal facts and preferences I currently remember:\n\n"
                    import json
                    msg += f"<pre>{json.dumps(memory_dict, ensure_ascii=False, indent=2)}</pre>"
                    msg += "\n\n<i>To add, change, or remove something, just write it in the chat (e.g. 'Forget about lunch time').</i>"
                    
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="settings_main")]])
            await callback.message.edit_text(msg, parse_mode="HTML", reply_markup=kb)
            await callback.answer()
        elif callback.data == "settings_timezone":
            await callback.message.edit_text("<b>Select your Timezone:</b>\n\nChoose from below, or just type your city/offset in the chat (e.g. 'Moscow', 'UTC+3', '+03:00') right now.", parse_mode="HTML", reply_markup=get_timezone_keyboard())
            await state.set_state(SettingsState.waiting_for_tz_text)
            await callback.answer()
        elif callback.data == "settings_reports":
            await callback.message.edit_text("<b>Report Destination:</b>\n\nWhere should I send your daily Evening Report?", parse_mode="HTML", reply_markup=get_reports_keyboard())
            await callback.answer()
        elif callback.data == "settings_close":
            await callback.message.delete()
            await callback.answer()
        elif callback.data in ["settings_back", "settings_main"]:
            await state.clear()
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                text = get_control_panel_text(user)
                await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
            await callback.answer()
        else:
            # Let it fall through to the other handlers at the bottom!
            return
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Callback error: {traceback.format_exc()}")
        await callback.answer(f"Error: {e}", show_alert=True)


@router.message(Command("settings"))
@router.message(lambda msg: msg.text == "⚙️ Settings")
async def cmd_settings(message: Message, command: CommandObject):
    """Update user preferences via config registry."""
    if not command.args:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            lines = ["<b>Current Settings:</b>"]
            for k, meta in USER_SETTINGS_REGISTRY.items():
                val = getattr(user, meta['db_column'])
                # Using HTML avoids telegram's aggressive parsing of literal underscores in variables
                lines.append(f"<code>{k}</code>: {html.escape(str(val))} (<i>{html.escape(str(meta['name']))}</i>)")
            lines.append("\n<i>To change settings, you can simply text me (e.g. 'set timezone to Europe/London').</i>")
            await message.answer("\n".join(lines), parse_mode="HTML")
        return

    parts = command.args.split(maxsplit=1)
    key = parts[0].lower()
    
    if key not in USER_SETTINGS_REGISTRY:
        await message.answer(f"Unknown setting <code>{html.escape(key)}</code>. Try <code>/settings</code> to see options.", parse_mode="HTML")
        return
        
    if len(parts) < 2:
        await message.answer(f"Error: Provide a value. Example: <code>/settings {html.escape(key)} 30</code>", parse_mode="HTML")
        return
        
    val_str = parts[1]
    meta = USER_SETTINGS_REGISTRY[key]
    
    try:
        if val_str.lower() == "none":
            val = None
        else:
            val = meta['type'](val_str)

        if key == "timezone" and val:
            import zoneinfo
            try:
                tz = zoneinfo.ZoneInfo(val)
                offset = datetime.datetime.now(tz).utcoffset().total_seconds() / 3600
                sign = "+" if offset >= 0 else ""
                offset_str = f"UTC{sign}{int(offset)}" if offset.is_integer() else f"UTC{sign}{int(offset)}:{int((abs(offset)*60)%60):02d}"
                val_str = f"{val} ({offset_str})"
            except Exception:
                raise ValueError(f"Invalid timezone format. Use IANA like 'Europe/Astrakhan'")
    except ValueError as e:
        await message.answer(f"Error: {e}", parse_mode="HTML")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        setattr(user, meta['db_column'], val)
        db.commit()
        await message.answer(f"✅ Setting <code>{key}</code> updated to <code>{html.escape(str(val_str))}</code>.", parse_mode="HTML")


