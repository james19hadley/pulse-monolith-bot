import aiogram
from aiogram import Router, F
from aiogram.types import Message
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user, log_tokens
from src.core.security import decrypt_key
from src.core.constants import IntentType
from src.ai.router import get_intent, extract_system_config, extract_entities, generate_chat, extract_log_habit, extract_log_work
from src.core.config import USER_SETTINGS_REGISTRY
from src.core.personas import get_persona_prompt
from src.bot.handlers.settings_keys import cmd_test_report

router = Router()

@router.message(F.text.startswith('/'))
async def handle_unknown_command(message: Message):
    await message.answer(f"Unknown command: <code>{message.text}</code>\n\nUse /help to see available commands.", parse_mode="HTML")

@router.message()
async def handle_freeform_text(message: Message):
    from aiogram.utils.chat_action import ChatActionSender
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
    
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
        
            keys = user.api_keys
            if not keys or user.llm_provider not in keys:
                await message.answer("Please configure an API key using `/add_key google await message.answer("Please configure an API key using `/add_key google <your_key>`", parse_mode="HTML")lt;your_keyawait message.answer("Please configure an API key using `/add_key google <your_key>`", parse_mode="HTML")gt;`", parse_mode="HTML")
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
            elif intent == IntentType.LOG_HABIT:
                return await _handle_log_habit(message, db, user, provider_name, real_api_key)
            elif intent == IntentType.LOG_WORK:
                return await _handle_log_work(message, db, user, provider_name, real_api_key)
            elif intent == IntentType.GENERATE_REPORT:
                return await cmd_test_report(message)
            elif intent == IntentType.ERROR:
                import html
                raw_err = str(error_msg) if error_msg else ""
                safe_err = html.escape(raw_err) if raw_err else "Unknown API error"
            
                if "429" in raw_err or "quota" in raw_err.lower():
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="🔑 Add / Change API Key", callback_data="settings_keys")
                    ]])
                    msg = (
                        "⚠️ <b>AI Provider Quota Exceeded</b>\n\n"
                        "It looks like you've hit the limit for the current API key. "
                        "Please add a new key or switch AI providers to continue."
                    )
                    await message.answer(msg, parse_mode="HTML", reply_markup=keyboard)
                else:
                    await message.answer(f"I encountered an error connecting to the AI provider.\n\nError details:\n<code>{safe_err}</code>", parse_mode="HTML")
            elif intent == IntentType.CHAT_OR_UNKNOWN:
                return await _handle_chat(message, db, user, provider_name, real_api_key)
            else:
                await message.answer(f"Intent detected: {intent.value}, but native implementation is missing currently.")

async def _handle_chat(message: Message, db, user, provider_name, api_key):
    import html
    persona_prompt = get_persona_prompt(user.persona_type, user.custom_persona_prompt, user.report_config)
    
    response_text, tokens = generate_chat(message.text, provider_name, api_key, persona_prompt)
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if response_text:
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
        habit = Habit(user_id=user.id, title=h.title)
        db.add(habit)
        db.flush()
        responses.append(f"✅ Habit created: <b>{habit.title}</b>")
        
    db.commit()
    await message.answer("\n".join(responses), parse_mode="HTML")

async def _handle_log_habit(message: Message, db, user, provider_name, api_key):
    from src.db.models import Habit
    from datetime import datetime, timezone

    # 1. Fetch active habits formatting for AI prompt
    habits = db.query(Habit).filter(Habit.user_id == user.id, Habit.status == 'active').all()
    if not habits:
        active_habits_text = "User has no active habits yet."
    else:
        active_habits_text = "User's active habits:\n" + "\n".join([f"ID: {h.id}, Title: {h.title}" for h in habits])

    # 2. Call AI extraction
    extraction, tokens = extract_log_habit(message.text, provider_name, api_key, active_habits_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction:
        await message.answer("I could not verify the exact habit to log.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if extraction.habit_id is None:
        title = extraction.unmatched_habit_name or "New Habit"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Click to Create", callback_data=f"create_habit_{title[:32]}")
        ]])
        await message.answer(f"🧩 I couldn't find a matching habit. Do you want to create <b>{title}</b>?", parse_mode="HTML", reply_markup=keyboard)
        return
        
    habit = db.query(Habit).filter_by(id=extraction.habit_id, user_id=user.id).first()
    if not habit:
        await message.answer("Error: AI returned an invalid Habit ID.")
        return

    # Log it
    habit.completions += extraction.amount_completed
    habit.last_completed_at = datetime.now(timezone.utc)
    db.commit()

    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\n💬 <i>{desc}</i>" if desc else ""
    
    # We could add an UNDO button here! User asked for it.
    # For undo, we would ideally track history, but for habits we can just allow them to undo the completion
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_habit_{habit.id}_{extraction.amount_completed}")
    ]])
    
    await message.answer(
        f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\n" \
        f"🏃 Total: {habit.completions}{append_desc}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def _handle_log_work(message: Message, db, user, provider_name, api_key):
    from src.db.models import Project, TimeLog
    from datetime import datetime, timezone

    # 1. Fetch active projects formatting for AI prompt
    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    if not projects:
        active_projects_text = "User has no active projects yet."
    else:
        active_projects_text = "User's active projects:\n" + "\n".join([f"ID: {p.id}, Title: {p.title}" for p in projects])

    # 2. Call AI extraction
    extraction, tokens = extract_log_work(message.text, provider_name, api_key, active_projects_text)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction:
        await message.answer("I could not verify the exact work/project to log.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if extraction.project_id is None:
        title = extraction.unmatched_project_name or "New Project"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Click to Create", callback_data=f"create_project_{title[:32]}")
        ]])
        await message.answer(f"🧩 I couldn't find a matching project. Do you want to create <b>{title}</b> first?", parse_mode="HTML", reply_markup=keyboard)
        return
        
    project = db.query(Project).filter_by(id=extraction.project_id, user_id=user.id).first()
    if not project:
        await message.answer("Error: AI returned an invalid Project ID.")
        return

    # Log it
    log_entry = TimeLog(
        user_id=user.id,
        project_id=project.id,
        duration_minutes=extraction.duration_minutes,
        description=extraction.description,
        is_manual=True,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc)
    )
    db.add(log_entry)
    project.total_minutes_spent += extraction.duration_minutes
    db.commit()
    db.refresh(log_entry)

    import html
    desc = html.escape(extraction.description) if extraction.description else ""
    append_desc = f"\n💬 <i>{desc}</i>" if desc else ""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_work_{log_entry.id}")
    ]])
    
    hours = extraction.duration_minutes / 60
    await message.answer(
        f"✅ Logged <b>{hours:g}h</b> to <b>{project.title}</b>!{append_desc}\n" \
        f"📈 Total: {project.total_minutes_spent / 60:g}h",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("create_habit_"))
async def cq_create_habit(callback: aiogram.types.CallbackQuery):
    title = callback.data.replace("create_habit_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        from src.db.models import Habit
        habit = Habit(user_id=user.id, title=title)
        db.add(habit)
        db.commit()
        db.refresh(habit)
        await callback.message.edit_text(f"✅ Habit created: <b>{habit.title}</b>! Try logging it again.", parse_mode="HTML")

@router.callback_query(F.data.startswith("undo_habit_"))
async def cq_undo_habit(callback: aiogram.types.CallbackQuery):
    _, _, hid_str, count_str = callback.data.split("_")
    hid = int(hid_str)
    count = int(count_str)
    
    with SessionLocal() as db:
        from src.db.models import Habit
        habit = db.query(Habit).filter_by(id=hid, user_id=callback.from_user.id).first()
        if habit and habit.completions >= count:
            habit.completions -= count
            db.commit()
            await callback.message.edit_text(f"↩️ Undid {count} completions for <b>{habit.title}</b>. Total is now {habit.completions}.", parse_mode="HTML")
        else:
            await callback.message.edit_text("❌ Could not undo (habit might not exist or count is too low).", parse_mode="HTML")

@router.callback_query(F.data.startswith("create_project_"))
async def cq_create_project(callback: aiogram.types.CallbackQuery):
    title = callback.data.replace("create_project_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        from src.db.models import Project
        project = Project(user_id=user.id, title=title)
        db.add(project)
        db.commit()
        db.refresh(project)
        await callback.message.edit_text(f"✅ Project created: <b>{project.title}</b>! Try logging time to it again.", parse_mode="HTML")

@router.callback_query(F.data.startswith("undo_work_"))
async def cq_undo_work(callback: aiogram.types.CallbackQuery):
    log_id_str = callback.data.replace("undo_work_", "")
    log_id = int(log_id_str)
    
    with SessionLocal() as db:
        from src.db.models import TimeLog, Project
        user = get_or_create_user(db, callback.from_user.id)
        log = db.query(TimeLog).filter_by(id=log_id, user_id=user.id).first()
        if log:
            project = db.query(Project).filter_by(id=log.project_id).first()
            if project:
                project.total_minutes_spent -= log.duration_minutes
                if project.total_minutes_spent < 0:
                    project.total_minutes_spent = 0
            
            db.delete(log)
            db.commit()
            await callback.message.edit_text(f"↩️ Undid {log.duration_minutes}m log.", parse_mode="HTML")
        else:
            await callback.message.edit_text("❌ Could not undo (log might not exist or already undone).", parse_mode="HTML")
