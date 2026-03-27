from src.core.config import USER_SETTINGS_REGISTRY
from src.core.personas import get_persona_prompt
import json
from aiogram.types import Message
from src.ai.router import generate_chat, extract_system_config, extract_report_config
from src.bot.handlers.utils import log_tokens
async def _handle_chat(message: Message, db, user, provider_name, api_key):
    import html
    persona_prompt = get_persona_prompt(user.persona_type, user.custom_persona_prompt, user.report_config)
    
    response_text, tokens = generate_chat(message.text, provider_name, api_key, persona_prompt)
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if response_text:
        # Check for pending_split close out in chat
        if user.active_session_id:
            from src.db.models import Session
            session = db.query(Session).filter(Session.id == user.active_session_id).first()
            if session and session.status == "pending_split":
                session.status = "closed"
                user.active_session_id = None
                db.commit()
                response_text += "\n\n<i>✅ Session closed. (Void time acknowledged)</i>"

        try:
            # We instructed the LLM to use strict HTML tags. 
            # Send raw response first, letting aiogram parse <b>, <i>, <code>.
            await message.answer(response_text, parse_mode="HTML")
        except Exception as e:
            # If the LLM still messed up HTML escaping (e.g. naked < or >), 
            # fallback to exact escaped text to preserve the message but lose styling.
            safe_response = html.escape(response_text)
            err_notice = "\n\n<i>(Formatting fallback engaged)</i>"
            await message.answer(safe_response + err_notice, parse_mode="HTML")
    else:
        await message.answer("I could not generate a response.")


async def _handle_config_update(message: Message, db, user, provider_name, api_key):
    settings_keys = list(USER_SETTINGS_REGISTRY.keys())
    extraction, tokens = extract_system_config(message.text, provider_name, api_key, settings_keys)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not extraction.settings:
        await message.answer("I could not determine the exact settings to update or the AI provider returned an error.")
        return
        
    responses = []
    import zoneinfo
    import datetime
    
    for update in extraction.settings:
        key = update.setting_key.lower()
        val = update.setting_value
        
        if key not in USER_SETTINGS_REGISTRY:
            responses.append(f"Ignored unknown setting {key}")
            continue
            
        meta = USER_SETTINGS_REGISTRY[key]
        try:
            cast_val = meta["type"](val)
            if key == "timezone":
                tz = zoneinfo.ZoneInfo(cast_val)
                offset = datetime.datetime.now(tz).utcoffset().total_seconds() / 3600
                sign = "+" if offset >= 0 else ""
                offset_str = f"UTC{sign}{int(offset)}" if offset.is_integer() else f"UTC{sign}{int(offset)}:{int((abs(offset)*60)%60):02d}"
                setattr(user, meta["db_column"], cast_val)
                responses.append(f"✅ Timezone updated to `{cast_val}` ({offset_str})")
            else:
                setattr(user, meta["db_column"], cast_val)
                responses.append(f"✅ `{key}` updated to `{cast_val}`")
        except Exception:
            responses.append(f"❌ Failed to parse value {val} for setting {key}")

    db.commit()
    await message.answer("\n".join(responses), parse_mode="HTML")



async def _handle_config_report(message: Message, db, user, provider_name, api_key):
    extraction, tokens = extract_report_config(message.text, provider_name, api_key)
    if tokens:
        from src.bot.handlers.utils import log_tokens
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction:
        await message.answer("I could not determine how to update your report configuration.")
        return
        
    # user.report_config is JSON stored in the db. 
    current_config = user.report_config or {}
    
    if extraction.blocks is not None:
        current_config["blocks"] = extraction.blocks
    if extraction.style is not None:
        current_config["style"] = extraction.style
        
    # Assign back to trigger SQLAlchemy mutation tracking
    # By replacing the dict entirely, it guarantees the update is detected.
    user.report_config = dict(current_config)
    db.commit()
    
    blocks_str = ", ".join(extraction.blocks)
    await message.answer(f"✅ Report configuration updated!\n<b>Blocks:</b> {blocks_str}\n<b>Style:</b> {extraction.style}", parse_mode="HTML")

