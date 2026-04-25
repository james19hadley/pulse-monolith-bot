"""
UI and Callbacks for customizing AI Talkativeness and Evening Reflection.

@Architecture-Map: [HND-SET-AICONV]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.bot.states import SettingsState
from src.bot.keyboards.settings import get_ai_conv_keyboard

router = Router()

@router.callback_query(F.data == "settings_ai_conv")
async def cq_settings_ai_conv(callback: CallbackQuery):
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        talk_level = getattr(user, 'talkativeness_level', 'standard') or 'standard'
        ref_config = getattr(user, 'reflection_config', {}) or {}
        
        await callback.message.edit_text(
            "<b>🗣 AI Conversation Settings</b>\n\n"
            "Adjust how chatty the AI is and what topics it focuses on during the Evening Reflection.",
            parse_mode="HTML",
            reply_markup=get_ai_conv_keyboard(talk_level, ref_config)
        )
    await callback.answer()

@router.callback_query(F.data.startswith("set_talk_"))
async def cq_set_talk(callback: CallbackQuery):
    level = callback.data.split("_")[2] # minimal, standard, coach
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        user.talkativeness_level = level
        db.commit()
        ref_config = getattr(user, 'reflection_config', {}) or {}
        await callback.message.edit_reply_markup(reply_markup=get_ai_conv_keyboard(level, ref_config))
    await callback.answer("Talkativeness updated!")

@router.callback_query(F.data.startswith("toggle_ref_"))
async def cq_toggle_ref(callback: CallbackQuery):
    topic = callback.data.split("_")[2] # wins, blockers, tomorrow
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        config = user.reflection_config or {}
        if isinstance(config, str):
            import json
            try: config = json.loads(config)
            except: config = {}
            
        key = f"focus_{topic}"
        config[key] = not config.get(key, False)
        
        user.reflection_config = config
        db.commit()
        
        talk_level = getattr(user, 'talkativeness_level', 'standard') or 'standard'
        await callback.message.edit_reply_markup(reply_markup=get_ai_conv_keyboard(talk_level, config))
    await callback.answer(f"Toggled {topic}!")

@router.callback_query(F.data == "set_ref_custom")
async def cq_set_ref_custom(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsState.waiting_for_custom_prompt)
    await callback.message.answer(
        "Send me the custom instructions for what I should ask you every evening.\n"
        "For example: <i>'Ask me if I exercised today and if I avoided scrolling shorts'</i>."
        "\n\nType /cancel to abort.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(SettingsState.waiting_for_custom_prompt)
async def process_custom_prompt(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Cancelled.")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        config = user.reflection_config or {}
        if isinstance(config, str):
            import json
            try: config = json.loads(config)
            except: config = {}
            
        config["custom_prompt"] = message.text
        user.reflection_config = config
        db.commit()
        
        talk_level = getattr(user, 'talkativeness_level', 'standard') or 'standard'
        
        await state.clear()
        await message.answer(
            "✅ Custom prompt saved. Here are your current AI Conversation settings:",
            reply_markup=get_ai_conv_keyboard(talk_level, config)
        )
