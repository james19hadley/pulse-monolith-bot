from aiogram import Router
from aiogram.types import Message
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user, log_tokens
from src.core.security import decrypt_key
from src.core.constants import IntentType
from src.ai.router import get_intent, extract_system_config, extract_entities
from src.core.config import USER_SETTINGS_REGISTRY
from src.bot.handlers.settings_keys import cmd_test_report

router = Router()

@router.message()
async def handle_freeform_text(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        keys = user.api_keys
        if not keys or user.llm_provider not in keys:
            await message.answer("Please configure an API key using `/add_key google <your_key>`", parse_mode="HTML")
            return

        active_key_data = keys[user.llm_provider]
        provider_name = active_key_data["provider"]
        real_api_key = decrypt_key(active_key_data["key"])

        intent, tokens, error_msg = get_intent(message.text, provider_name, real_api_key)
        if tokens:
            log_tokens(db, message.from_user.id, tokens)

        if intent == IntentType.SYSTEM_CONFIG:
            return await _handle_config_update(message, db, user, provider_name, real_api_key)
        elif intent == IntentType.CREATE_ENTITIES:
            return await _handle_create_entities(message, db, user, provider_name, real_api_key)
        elif intent == IntentType.LOG_WORK:
            await message.answer("Please use <code>/log &lt;minutes&gt; [description]</code> to log time.", parse_mode="HTML")
        elif intent == IntentType.GENERATE_REPORT:
            return await cmd_test_report(message)
        elif intent == IntentType.ERROR:
            import html
            safe_err = html.escape(str(error_msg)) if error_msg else "Unknown API error"
            await message.answer(f"I encountered an error connecting to the AI provider.\n\nError details:\n<code>{safe_err}</code>", parse_mode="HTML")
        else:
            await message.answer(f"Intent detected: {intent.value}, but native implementation is missing currently.")

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

async def _handle_create_entities(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, Habit
    extraction, tokens = extract_entities(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or (not extraction.projects and not extraction.habits):
        await message.answer("I could not determine the exact details for the project or habit to create.")
        return
        
    responses = []
    
    for p in extraction.projects:
        proj = Project(user_id=user.id, title=p.title, status="active", target_minutes=p.target_minutes)
        db.add(proj)
        db.flush()
        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_minutes > 0:
            msg += f" (Target: {proj.target_minutes / 60:g}h)"
        responses.append(msg)
        
    for h in extraction.habits:
        habit = Habit(user_id=user.id, title=h.title, status="active")
        db.add(habit)
        db.flush()
        responses.append(f"✅ Habit created: <b>{habit.title}</b>")
        
    db.commit()
    await message.answer("\n".join(responses), parse_mode="HTML")
