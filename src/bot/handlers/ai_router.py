import json
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.db.repo import SessionLocal
from src.bot.texts import Prompts
from src.bot.handlers.utils import get_or_create_user, log_tokens
from src.ai.router import IntentType, get_intent
from src.ai.providers import GoogleProvider

# --- NEW DISPATCHER IMPORTS ---
from src.bot.handlers.intents.intent_core import _handle_chat, _handle_config_update, _handle_config_report, _handle_undo
from src.bot.handlers.intents.intent_entities import _handle_create_entities, _handle_add_inbox, _handle_add_tasks, _handle_edit_entities
from src.bot.handlers.intents.intent_log_work import _handle_log_work
from src.bot.handlers.intents.intent_log_habit import _handle_log_habit
from src.bot.handlers.intents.intent_session import _handle_session_control
# _handle_log_work, _handle_log_habit, _handle_session_control

router = Router()
logger = logging.getLogger(__name__)

INTENT_HANDLERS = {
    IntentType.CHAT_OR_UNKNOWN: _handle_chat,
    IntentType.LOG_WORK: _handle_log_work,
    IntentType.LOG_HABIT: _handle_log_habit,
    IntentType.SESSION_CONTROL: _handle_session_control,
    
    IntentType.CREATE_ENTITIES: _handle_create_entities,
    IntentType.ADD_INBOX: _handle_add_inbox,
    IntentType.ADD_TASKS: _handle_add_tasks,
    IntentType.SYSTEM_CONFIG: _handle_config_update,
    IntentType.CONFIG_REPORT: _handle_config_report,
    IntentType.EDIT_ENTITIES: _handle_edit_entities,
    IntentType.UNDO: _handle_undo,
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

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

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
            intent, tokens, err = get_intent(message.text, provider_name, api_key)
            if tokens:
                log_tokens(db, user.telegram_id, tokens)
                
            if err or intent == IntentType.ERROR:
                logger.error(f"Routing Error: {err}")
                if err and ("API key" in str(err) or "API_KEY" in str(err) or "api_key" in str(err).lower() or "400" in str(err)):
                    await message.answer("⚠️ Неверный API ключ для выбранного провайдера. Пожалуйста, проверьте его в настройках.\n\nОтладка: " + str(err))
                else:
                    await message.answer(Prompts.ERROR_GLOBAL + f"\n\nОтладка LLM: {err}")
                return
            
            if intent == IntentType.UNKNOWN_PROVIDER:
                await message.answer(Prompts.UNKNOWN_COMMAND.format(text=message.text))
                return
                
            logger.info(f"User {user.telegram_id} intent localized: {intent}")
            
            # --- NEW DISPATCH ROUTER ---
            handler = INTENT_HANDLERS.get(intent)
            if handler:
                await handler(message, db, user, provider_name, api_key)
            else:
                await message.answer(Prompts.UNKNOWN_COMMAND.format(text=message.text))
                
        except Exception as e:
            logger.error(f"Routing Error: {e}", exc_info=True)
            await message.answer(Prompts.ERROR_GLOBAL + f"\n\nОтладка Системы: {str(e)}")
