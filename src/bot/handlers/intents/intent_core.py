"""
Execution mapping for NLP intents classified by AI (links intents to actual functions).

@Architecture-Map: [HND-INTENT-CORE]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from src.core.config import USER_SETTINGS_REGISTRY
from src.core.personas import get_persona_prompt
import json
from aiogram.types import Message
from src.ai.router import generate_chat, extract_system_config, extract_report_config, extract_update_memory
from src.bot.handlers.utils import log_tokens

async def _handle_update_memory(message: Message, db, user, provider_name, api_key):
    extraction, tokens = extract_update_memory(message.text, provider_name, api_key)
    if tokens:
        log_tokens(db, user.telegram_id, tokens)
        
    if not extraction:
        await message.answer("I couldn't figure out exactly what to remember.")
        return
        
    mem_key = extraction.memory_key
    mem_val = extraction.memory_value
    
    current_memory = user.user_memory or {}
    
    # If they want to forget something (value is empty or negative), delete the key
    if mem_val.lower() in ["none", "null", "forget", "delete", ""]:
        if mem_key in current_memory:
            del current_memory[mem_key]
            msg = f"🧠 Забыл факт: <b>{mem_key}</b>"
        else:
            msg = f"🧠 Я и так не помнил: <b>{mem_key}</b>"
    else:
        current_memory[mem_key] = mem_val
        msg = f"🧠 Запомнил:\n<b>{mem_key}</b> = <i>{mem_val}</i>"
        
    user.user_memory = current_memory
    db.commit()
    await message.answer(msg, parse_mode="HTML")

async def _handle_project_status(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project
    import html
    
    # We will just fetch active projects and ask LLM which one they mean, or we can just list all active projects for now.
    active_projs = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
    if not active_projs:
        await message.answer("У вас нет активных проектов.")
        return
        
    # Temporary fallback until we build a full project search parameter extractor:
    # Just render the standard /projects list.
    from src.bot.handlers.core import cmd_projects
    await cmd_projects(message)

async def _handle_chat(message: Message, db, user, provider_name, api_key):
    import html
    
    # Context Injection for smart NLP
    from src.db.models import Project, Task
    active_projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    # TRUNCATE PENDING TASKS to avoid massive LLM context explosion which causes high latency
    pending_tasks = db.query(Task).filter(Task.user_id == user.id, Task.status == 'pending').limit(10).all()
    
    context_str = ""
    if active_projects or pending_tasks:
        context_str = "\n\nUSER's CURRENT ENTITIES (For your awareness):\n"
        if active_projects:
            context_str += "Active Projects:\n" + "\n".join([f"- {p.title} (ID: {p.id})" for p in active_projects]) + "\n"
        if pending_tasks:
            context_str += "Pending Tasks:\n" + "\n".join([f"- {t.title} (ID: {t.id})" for t in pending_tasks]) + "\n"
    
    persona_prompt = get_persona_prompt(user.persona_type, user.custom_persona_prompt, user.report_config, getattr(user, "talkativeness_level", "standard"))
    
    if user.active_session_id:
        persona_prompt += "\n\n[SYSTEM NOTICE]: The user is currently in an active focus session. If they describe what they are currently working on or what they just finished (e.g. answering a 'what are you doing' nudge), you MUST include the exact string `[CHUNK_LOG]` in your response. This will signal the system to log the elapsed time as a chunk."
        
    persona_prompt += context_str
    
    response_text, tokens = generate_chat(message.text, provider_name, api_key, persona_prompt)
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if response_text:
        # Check for smart chunk
        if "[CHUNK_LOG]" in response_text and user.active_session_id:
            response_text = response_text.replace("[CHUNK_LOG]", "").strip()
            from src.db.models import Session, TimeLog
            import datetime
            session = db.query(Session).filter(Session.id == user.active_session_id).first()
            if session:
                last_log = db.query(TimeLog).filter(TimeLog.session_id == session.id).order_by(TimeLog.created_at.desc()).first()
                start_ref = last_log.created_at if last_log else session.start_time
                now = datetime.datetime.utcnow()
                elapsed_mins = int((now - start_ref).total_seconds() / 60)
                
                if elapsed_mins > 0:
                    from src.bot.handlers.utils import get_or_create_project_zero
                    p_zero = get_or_create_project_zero(db, user.id)
                    chunk = TimeLog(
                        user_id=user.id,
                        session_id=session.id,
                        duration_minutes=elapsed_mins,
                        project_id=p_zero.id,
                        description=message.text[:200], # Save their response as the description
                        created_at=now
                    )
                    db.add(chunk)
                    p_zero.current_value = (p_zero.current_value or 0) + elapsed_mins
                    if p_zero.daily_target_value is not None:
                        p_zero.daily_progress = (p_zero.daily_progress or 0) + elapsed_mins
                    db.commit()
                    response_text += f"\n\n<i>⏱ Logged {elapsed_mins} minutes to this session chunk.</i>"
                    
        # Check for pending_split close out in chat
        if user.active_session_id:
            from src.db.models import Session
            session = db.query(Session).filter(Session.id == user.active_session_id).first()
            if session and session.status == "pending_split":
                session.status = "closed"
                user.active_session_id = None
                db.commit()
                response_text += "\n\n<i>✅ Session closed. (Routine time acknowledged)</i>"

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



async def _handle_undo(message: Message, db, user, provider_name, api_key):
    from src.bot.handlers.core import cmd_undo
    # Since cmd_undo uses SessionLocal anyway, we can just call it
    # We pass None for state since it handles it
    await cmd_undo(message, state=None)
