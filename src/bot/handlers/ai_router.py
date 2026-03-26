import json
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.db.session import SessionLocal
from src.db.repo import get_or_create_user, get_project_by_name, get_habit_by_name, delete_entity, create_action, update_project_progress, log_tokens
from src.db.models import ActionType
from src.core.prompts import system_prompt, unknown_command_message, error_message, generate_intent_prompt
from src.ai.router import IntentType
from src.ai.providers import GoogleProvider

# --- NEW DISPATCHER IMPORTS ---
from src.bot.handlers.intents.intent_core import _handle_chat, _handle_config_update
from src.bot.handlers.intents.intent_entities import _handle_create_entities, _handle_add_inbox
from src.bot.handlers.intents.intent_tracker import _handle_log_work, _handle_log_habit

router = Router()
logger = logging.getLogger(__name__)

INTENT_HANDLERS = {
    IntentType.CHAT: _handle_chat,
    IntentType.LOG_WORK: _handle_log_work,
    IntentType.LOG_HABIT: _handle_log_habit,
    IntentType.CREATE_PROJECT: _handle_create_entities,
    IntentType.CREATE_HABIT: _handle_create_entities,
    IntentType.CATCH_TO_INBOX: _handle_add_inbox,
    IntentType.CONFIG_UPDATE: _handle_config_update,
}

@router.message()
async def ai_message_router(message: Message):
    """
    The central intelligence router.
    Every raw message comes here first. We ask the LLM 'What does the user want to do?'
    and then route it to the appropriate specialized function.
    """
    if message.text.startswith('/'):
        return

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        provider_name = user.llm_provider
        api_key = None
        
        # We handle api keys securely
        keys = getattr(user, "api_keys", None)
        if keys and provider_name in keys:
            from src.core.security import decrypt_key
            try:
                api_key = decrypt_key(keys[provider_name]["key"])
            except Exception:
                pass
                
        if not api_key:
            await message.answer("⚠️ You haven't configured an API key for your chosen AI provider yet.\nPlease use the web dashboard or /settings.")
            return

        try:
            # We must parse intent using the provider
            provider = GoogleProvider(api_key=api_key)
            prompt = generate_intent_prompt(message.text)
            response, tokens = provider.generate_structured_response(prompt, "IntentRouterSchema")
            log_tokens(db, user.telegram_id, tokens)
            
            if not response or not response.intent:
                await message.answer(unknown_command_message())
                return
            
            intent = response.intent
            logger.info(f"User {user.telegram_id} intent localized: {intent}")
            
            # --- NEW DISPATCH ROUTER ---
            handler = INTENT_HANDLERS.get(intent)
            if handler:
                if intent == IntentType.UNDO_LAST_ACTION:
                    pass # Handled via callbacks usually, but if typed it would go to a special function
                else:
                    await handler(message, db, user, provider_name, api_key)
            else:
                await message.answer(unknown_command_message())
                
        except Exception as e:
            logger.error(f"Routing Error: {e}", exc_info=True)
            await message.answer(error_message())


@router.callback_query(F.data.startswith("undo_"))
async def cq_undo_work(callback: CallbackQuery):
    action_id = int(callback.data.split("_")[1])
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        # Fetch the action to see what it was
        action = db.query(Action).filter(Action.id == action_id, Action.user_id == user.id).first()
        if not action:
            await callback.answer("Action not found or already undone.")
            return
            
        # Revert logic based on type
        if action.action_type == ActionType.LOG_WORK and action.project_id:
            project = db.query(Project).filter(Project.id == action.project_id).first()
            if project:
                project.current_hours -= action.value
                
        elif action.action_type == ActionType.LOG_HABIT and action.habit_id:
            pass # Usually habits are just logs, nothing to decrement unless tracking streaks
            
        db.delete(action)
        db.commit()
        
    await callback.message.edit_text(f"✅ Action undone successfully.")
    await callback.answer()
