import json
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession
from src.db.models import User
from src.ai.providers import GoogleProvider
from src.bot.views import unknown_command_message

async def _handle_chat(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.CHAT - conversational persona"""
    provider = GoogleProvider(api_key=api_key)
    
    from src.core.personas import get_persona_prompt
    persona_sys = get_persona_prompt(user.persona_type, user.custom_persona_prompt)
    
    response, tokens = provider.generate_chat_response(message.text, persona_sys)
    from src.bot.handlers.utils import log_tokens
    log_tokens(db, user.telegram_id, tokens)
    
    if response:
        await message.answer(response)
    else:
        await message.answer(unknown_command_message())

async def _handle_config_update(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.CONFIG_UPDATE - e.g. 'Set my persona to strict' or 'I live in UTC+2'"""
    # ...existing implementation will go here...
    provider = GoogleProvider(api_key=api_key)
    
    prompt = f"The user wants to update their bot settings. Extract the configuration from: '{message.text}'"
    response, tokens = provider.generate_structured_response(prompt, "ConfigUpdateParams")
    from src.bot.handlers.utils import log_tokens
    log_tokens(db, user.telegram_id, tokens)
    
    if not response:
        await message.answer("I couldn't understand what setting you want to change.")
        return
        
    changes = []
    if getattr(response, "timezone", None):
        user.timezone = response.timezone
        changes.append(f"Timezone: {user.timezone}")
    if getattr(response, "day_cutoff_time", None):
        from datetime import time
        try:
            h, m = map(int, response.day_cutoff_time.split(":"))
            user.day_cutoff_time = time(h, m)
            changes.append(f"Day Cutoff: {user.day_cutoff_time.strftime('%H:%M')}")
        except Exception:
            pass
    if getattr(response, "persona_type", None):
        user.persona_type = response.persona_type
        changes.append(f"Persona: {user.persona_type}")
        
    if changes:
        db.commit()
        await message.answer("✅ Settings updated:\n- " + "\n- ".join(changes))
    else:
        await message.answer("No actionable settings found.")

async def _handle_config_report(message: Message, db: DBSession, user: User, provider_name: str, api_key: str):
    """Handles IntentType.CONFIG_REPORT"""
    # Coming soon in Sprint 19!
    await message.answer("You've hit the report config intent, which is currently being built! Stay tuned.")

