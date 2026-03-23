import datetime
import html
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import func

from src.db.repo import SessionLocal
from src.db.models import User, TokenUsage, TimeLog, Habit, Inbox, Project
from src.core.config import USER_SETTINGS_REGISTRY
from src.bot.views import stats_message, build_daily_report
from src.core.security import encrypt_key, decrypt_key
from src.ai.providers import GoogleProvider
from src.bot.handlers.utils import get_or_create_user

router = Router()

@router.message(Command("add_key"))
async def cmd_add_key(message: Message, command: CommandObject):
    """
    Saves the user's personal API key securely.
    Usage: /add_key <provider> <your_api_key> [alias_name]
    """
    if not command.args:
        await message.answer("Usage: <code>/add_key &lt;provider&gt; &lt;your_api_key&gt; [alias]</code>\nAvailable providers: <code>google</code>, <code>openai</code>, <code>anthropic</code>\nExample: <code>/add_key google AIzaSy... my_google_2</code>", parse_mode="HTML")
        return
        
    parts = command.args.strip().split()
    if len(parts) < 2:
        await message.answer("Error: You must specify both the provider and the key.\nExample: <code>/add_key google AIzaSy...</code>", parse_mode="HTML")
        return
        
    provider, api_key = parts[0].lower(), parts[1]
    # Use the alias if provided, otherwise the provider name
    alias = parts[2].lower() if len(parts) > 2 else provider
    
    if provider not in ["google", "openai", "anthropic"]:
        await message.answer("Error: Unsupported provider. Choose from: <code>google</code>, <code>openai</code>, <code>anthropic</code>", parse_mode="HTML")
        return
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        keys[alias] = {
            "provider": provider,
            "key": encrypt_key(api_key)
        }
        user.set_api_keys(keys)
        user.llm_provider = alias # Set this alias as the active one
        db.commit()
        
    await message.answer(f"API Key for provider '{provider}' successfully saved under alias '{alias}'. It is now active.")

@router.message(Command("delete_key"))
async def cmd_delete_key(message: Message, command: CommandObject):
    """Deletes a saved API key (by alias)."""
    alias_to_delete = command.args.strip().lower() if command.args else None
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        
        if not keys:
            await message.answer("You do not have any saved API keys.")
            return
            
        if not alias_to_delete:
            await message.answer("Usage: <code>/delete_key &lt;alias&gt;</code>\nSaved aliases: " + ", ".join(keys.keys()), parse_mode="HTML")
            return
            
        if alias_to_delete not in keys:
            await message.answer(f"No key saved for alias '{alias_to_delete}'.")
            return
            
        del keys[alias_to_delete]
        user.set_api_keys(keys)
        # If we deleted the active provider, fallback to one of the others or google
        if user.llm_provider == alias_to_delete:
            user.llm_provider = list(keys.keys())[0] if keys else "google"
            
        db.commit()
        
    await message.answer(f"Your API key '{alias_to_delete}' has been deleted.")

@router.message(Command("my_key"))
async def cmd_my_key(message: Message):
    """Checks the status of the user's current aliases."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        if keys:
            providers = ", ".join(f"<code>{k}</code>" for k in keys.keys())
            await message.answer(f"<b>Saved Keys (Aliases):</b> {providers}\n<b>Active AI Alias:</b> <code>{user.llm_provider}</code>\n\n<i>To switch your active key, you can use</i> <code>/use_key &lt;alias-name&gt;</code>", parse_mode="HTML")
        else:
            await message.answer("Status: No API key configured. Features limited. Use <code>/add_key google &lt;your_key&gt;</code>.", parse_mode="HTML")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Shows AI Token Usage"""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        prompt_total = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        comp_total = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        
        cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30
        
        await message.answer(
            stats_message(prompt_total, comp_total, cost),
            parse_mode="HTML"
        )

@router.message(Command("settings"))
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

@router.message(Command("test_report"))
async def cmd_test_report(message: Message):
    """Developer command to instantly generate an accountability report."""
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        now = datetime.datetime.utcnow()
        last_24h = now - datetime.timedelta(hours=24)
        
        config = user.report_config
        if isinstance(config, str):
            import json
            try:
                config = json.loads(config)
            except Exception:
                config = None
        if not config:
            config = {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
        
        user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= last_24h).all()
        focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
        void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
        
        proj_stats = {}
        for log in user_logs:
            if log.project_id:
                proj = db.query(Project).filter(Project.id == log.project_id).first()
                if proj:
                    proj_stats[proj.title] = proj_stats.get(proj.title, 0) + log.duration_minutes
                
        user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value} for h in user_habits]
        
        inbox_items = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").count()
        
        stats = {
            "date": now.strftime("%Y-%m-%d (Test)"),
            "focus_minutes": focus_time,
            "void_minutes": void_time,
            "projects": proj_stats,
            "habits": habits_data,
            "inbox_count": inbox_items
        }
        
        ai_comment = None
        keys = user.api_keys
        if keys and user.llm_provider in keys:
            active_key_data = keys[user.llm_provider]
            if active_key_data["provider"] == "google":
                try:
                    provider = GoogleProvider(api_key=decrypt_key(active_key_data["key"]))
                    prompt = f"Write a 1-sentence {user.persona_type} style comment for this end-of-day report. Just output the sentence."
                    response = provider.client.models.generate_content(model=provider.model_id, contents=prompt)
                    ai_comment = response.text
                except Exception as e:
                    print(f"Failed to generate AI comment: {e}")
                
        report_text = build_daily_report(stats, config, ai_comment)
        await message.answer(report_text, parse_mode="HTML")

@router.message(Command("use_key"))
async def cmd_use_key(message: Message, command: CommandObject):
    """Switches the active API key alias."""
    if not command.args:
        await message.answer("Usage: <code>/use_key &lt;alias&gt;</code>", parse_mode="HTML")
        return
        
    alias = command.args.strip().lower()
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        
        if not keys or alias not in keys:
            await message.answer(f"Error: You do not have a key saved under the alias <code>{alias}</code>. Use <code>/my_key</code> to view your aliases.", parse_mode="HTML")
            return
            
        user.llm_provider = alias
        db.commit()
        
    await message.answer(f"✅ Active AI provider switched to <code>{alias}</code>", parse_mode="HTML")
