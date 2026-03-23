import datetime
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from src.db.repo import SessionLocal
from src.db.models import User, Session, Project, TimeLog, Habit, Inbox, ActionLog, TokenUsage
from src.core.constants import IntentType
from src.core.config import USER_SETTINGS_REGISTRY
from src.bot.views import (
    welcome_message, 
    session_started_message, 
    session_already_active_message,
    no_active_session_message,
    session_ended_message,
    project_created_message,
    project_list_message,
    stats_message,
    settings_list_message,
    habit_created_message,
    habit_updated_message,
    inbox_saved_message,
    undo_success_message,
    undo_fail_message,
    nothing_to_undo_message,
    build_daily_report
)
from src.core.security import encrypt_key, decrypt_key
from src.ai.router import (
    get_intent, extract_log_work, extract_log_habit, extract_inbox, extract_session_control, extract_report_config
)
from src.ai.providers import GoogleProvider

router = Router()

def get_or_create_user(db: DBSession, telegram_id: int) -> User:
    """Utility function to create user on first interaction."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.message(Command("start"))
async def cmd_start(message: Message):
    # In an MVP we use synchronous DB calls. For heavy traffic, 
    # we would use asyncio.to_thread or SQLAlchemy async drivers.
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        has_key = user.api_key_encrypted is not None
        
    await message.answer(welcome_message(has_key))

@router.message(Command("start_session"))
async def cmd_start_session(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        # Check if user already has an active session
        active_session = db.query(Session).filter(
            Session.user_id == user.id, 
            Session.status == "active"
        ).first()
        
        if active_session:
            await message.answer(session_already_active_message())
            return
            
        # Create a new session
        new_session = Session(user_id=user.id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # Link it to the user's active session tracker
        user.active_session_id = new_session.id
        db.commit()
        
    await message.answer(session_started_message())

@router.message(Command("end_session"))
async def cmd_end_session(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        active_session = db.query(Session).filter(
            Session.id == user.active_session_id,
            Session.status == "active"
        ).first()
        
        if not active_session:
            await message.answer(no_active_session_message())
            return
            
        # Close the session by marking end time and status
        active_session.end_time = datetime.datetime.utcnow()
        active_session.status = "closed"
        user.active_session_id = None
        
        # Calculate duration in minutes Math
        duration = active_session.end_time - active_session.start_time
        # Round up seconds to the nearest minute or use total_seconds properly
        total_minutes = int(duration.total_seconds() / 60)
        # If it's less than a minute, show 1 minute so the user knows they tracked *something*
        if total_minutes == 0 and duration.total_seconds() > 0:
            total_minutes = 1
            
        # Calculate Focused Time
        focus_time_result = db.query(func.sum(TimeLog.duration_minutes)).filter(
            TimeLog.session_id == active_session.id
        ).scalar()
        focus_minutes = focus_time_result if focus_time_result else 0
        
        # Calculate The Void
        void_minutes = total_minutes - focus_minutes
        if void_minutes < 0:
            void_minutes = 0
            
        db.commit()
        
    await message.answer(session_ended_message(total_minutes, focus_minutes, void_minutes), parse_mode="Markdown")

@router.message(Command("set_key"))
async def cmd_set_key(message: Message, command: CommandObject):
    """Saves the user's personal API key securely to the database."""
    if not command.args:
        await message.answer("Usage: `/set_key <provider> <your_api_key>`\nAvailable providers: `google`, `openai`, `anthropic`", parse_mode="Markdown")
        return
        
    parts = command.args.strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Error: You must specify both the provider and the key.\nExample: `/set_key google AIzaSy...`", parse_mode="Markdown")
        return
        
    provider, api_key = parts[0].lower(), parts[1]
    
    if provider not in ["google", "openai", "anthropic"]:
        await message.answer("Error: Unsupported provider. Choose from: `google`, `openai`, `anthropic`", parse_mode="Markdown")
        return
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        # Encrypt the key before saving it to the database
        user.api_key_encrypted = encrypt_key(api_key)
        user.llm_provider = provider
        db.commit()
        
    await message.answer(f"API Key for provider '{provider}' successfully encrypted and secured in the database. I will use it for processing protocols.")

@router.message(Command("delete_key"))
async def cmd_delete_key(message: Message):
    """Deletes the user's saved API key."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        if not user.api_key_encrypted:
            await message.answer("You do not have any active API key to delete.")
            return
            
        user.api_key_encrypted = None
        user.llm_provider = "google" # Reset to default
        db.commit()
        
    await message.answer("Your API key has been deleted from the database.")

@router.message(Command("my_key"))
async def cmd_my_key(message: Message):
    """Checks the status of the user's current key."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        if user.api_key_encrypted:
            await message.answer(f"Status: Key is configured.\nActive AI Provider: `{user.llm_provider}`", parse_mode="Markdown")
        else:
            await message.answer("Status: No API key configured. Features limited. Use `/set_key` to add one.", parse_mode="Markdown")

@router.message(Command("projects"))
async def cmd_projects(message: Message):
    """Lists all active projects."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        active_projects = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
        
    await message.answer(project_list_message(active_projects), parse_mode="Markdown")

@router.message(Command("new_project"))
async def cmd_new_project(message: Message, command: CommandObject):
    """Creates a new active project."""
    if not command.args:
        await message.answer("Usage: `/new_project <Project Title>`", parse_mode="Markdown")
        return
        
    title = command.args.strip()
    if len(title) > 100:
        await message.answer("Error: Project title too long (max 100 chars).")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        new_proj = Project(
            user_id=user.id,
            title=title,
            status="active"
        )
        db.add(new_proj)
        db.commit()
        await message.answer(project_created_message(new_proj.id, new_proj.title), parse_mode="Markdown")

@router.message(Command("new_habit"))
async def cmd_new_habit(message: Message, command: CommandObject):
    """Creates a new tracking habit."""
    if not command.args:
        await message.answer("Usage: `/new_habit <Target Number> <Title>`\nExample: `/new_habit 20 Pushups`", parse_mode="Markdown")
        return
        
    parts = command.args.split(maxsplit=1)
    if len(parts) < 2 or not parts[0].isdigit():
        await message.answer("Error: Provide target number then title. Example: `/new_habit 10 Reading pages`", parse_mode="Markdown")
        return
        
    target_value = int(parts[0])
    title = parts[1].strip()
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        new_habit = Habit(
            user_id=user.id,
            title=title,
            target_value=target_value
        )
        db.add(new_habit)
        db.commit()
        await message.answer(habit_created_message(new_habit.id, new_habit.title, new_habit.target_value), parse_mode="Markdown")

@router.message(Command("settings"))
async def cmd_settings(message: Message, command: CommandObject):
    """Update user preferences via config registry."""
    if not command.args:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            
            settings_list = []
            for key, meta in USER_SETTINGS_REGISTRY.items():
                val = getattr(user, meta['db_column'])
                if val is None:
                    val = meta['default']
                settings_list.append({"key": key, "name": meta['name'], "val": val, "desc": meta['description']})
                
            await message.answer(settings_list_message(settings_list), parse_mode="Markdown")
        return

    parts = command.args.split(maxsplit=1)
    key = parts[0].lower()
    
    if key not in USER_SETTINGS_REGISTRY:
        await message.answer(f"Unknown setting '{key}'. Try `/settings` to see options.", parse_mode="Markdown")
        return
        
    if len(parts) < 2:
        await message.answer(f"Error: Provide a value. Example: `/settings {key} 30`", parse_mode="Markdown")
        return
        
    val_str = parts[1]
    meta = USER_SETTINGS_REGISTRY[key]
    
    try:
        if val_str.lower() == "none":
            val = None
        else:
            val = meta['type'](val_str)
    except ValueError:
        await message.answer(f"Error: Value must be of type {meta['type'].__name__}.", parse_mode="Markdown")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        setattr(user, meta['db_column'], val)
        db.commit()
        await message.answer(f"✅ Setting `{key}` updated to `{val}`.", parse_mode="Markdown")

def log_tokens(telegram_id: int, usage_data: dict):
    if not usage_data: return
    try:
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                tu = TokenUsage(
                    user_id=user.id,
                    prompt_tokens=usage_data.get('prompt_tokens', 0),
                    completion_tokens=usage_data.get('completion_tokens', 0),
                    total_tokens=usage_data.get('total_tokens', 0),
                    model_name=usage_data.get('model_name', 'unknown')
                )
                db.add(tu)
                db.commit()
    except Exception as e:
        print(f"Error logging tokens: {e}")

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
            parse_mode="Markdown"
        )


@router.message(Command("test_report"))
async def cmd_test_report(message: Message):
    """Developer command to instantly generate an accountability report regardless of the hour."""
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        now = datetime.datetime.utcnow()
        last_24h = now - datetime.timedelta(hours=24)
        config = user.report_config if user.report_config else {"blocks": ["focus", "habits", "inbox", "void"], "style": "emoji"}
        
        user_logs = db.query(TimeLog).filter(TimeLog.user_id == user.id, TimeLog.created_at >= last_24h).all()
        focus_time = sum(l.duration_minutes for l in user_logs if l.project_id is not None)
        void_time = sum(l.duration_minutes for l in user_logs if l.project_id is None)
        
        proj_stats = {}
        for log in user_logs:
            if log.project_id:
                proj = db.query(Project).filter(Project.id == log.project_id).first()
                p_title = proj.title if proj else "Unknown Project"
                proj_stats[p_title] = proj_stats.get(p_title, 0) + log.duration_minutes
                
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
        if user.api_key_encrypted and user.llm_provider == "google":
            try:
                provider = GoogleProvider(api_key=decrypt_key(user.api_key_encrypted))
                prompt = f"Write a 1-sentence {user.persona_type} style comment for this end-of-day report. Just output the sentence."
                response = provider.client.models.generate_content(model=provider.model_id, contents=prompt)
                ai_comment = response.text
            except Exception as e:
                print(f"Failed to generate AI comment: {e}")
                
        report_text = build_daily_report(stats, config, ai_comment)
        await message.answer(report_text, parse_mode="Markdown")

@router.message(F.forward_from_chat)
async def cmd_bind_channel_via_forward(message: Message):
    """Allows user to bind a channel simply by forwarding any message from it."""
    if message.forward_from_chat.type == "channel":
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.target_channel_id = channel_id
            db.commit()
        await message.answer(f"✅ Awesome! I have bound your accountability reports to the channel: **{channel_title}**", parse_mode="Markdown")

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_ADMIN, IS_NOT_MEMBER

@router.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdated):
    """Automatically bind a channel if the bot is added to it."""
    if event.chat.type == "channel":
        if event.new_chat_member.status in ["administrator", "member", "creator"]:
            with SessionLocal() as db:
                user = get_or_create_user(db, event.from_user.id)
                user.target_channel_id = event.chat.id
                db.commit()
            try:
                await event.bot.send_message(
                    event.from_user.id,
                    f"✅ I noticed you added me to the channel **{event.chat.title}**!\nI\'ve automatically set it as your target.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

@router.message(F.text)
async def handle_freeform_text(message: Message):
    """
    Catch-all handler for plain text. 
    It checks if the user has an API key, decrypts it, and then asks the LLM to classify the intent.
    """
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        if not user.api_key_encrypted:
            await message.answer("Error: You must configure an API key first. Use /set_key <your_gemini_api_key>")
            return
            
        # Decrypt key to use it
        try:
            api_key = decrypt_key(user.api_key_encrypted)
        except Exception as e:
            await message.answer("Error: Key decryption failed. Please set your key again.")
            return
            
        provider = user.llm_provider
    
    # Let the user know the Monolith is "thinking"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    intent, i_usage = get_intent(message.text, provider, api_key)
    log_tokens(message.from_user.id, i_usage)
    
    if intent == IntentType.LOG_WORK:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            active_session = db.query(Session).filter(
                Session.user_id == user.id, 
                Session.status == "active"
            ).first()
            
            if not active_session:
                await message.answer("⚠️ You cannot log work without an active session. Use /start_session first.")
                return

            active_projects = db.query(Project).filter(Project.user_id == user.id, Project.status == "active").all()
            if not active_projects:
                projects_text = "No active projects found."
            else:
                projects_text = "\n".join([f"ID: {p.id} | Title: {p.title}" for p in active_projects])

            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            params, p_usage = extract_log_work(message.text, provider, api_key, projects_text)
            log_tokens(message.from_user.id, p_usage)

            if not params:
                await message.answer("❌ Error interpreting parameters from your work log.")
                return
            
            # Verify the project belongs to the user if an ID was returned
            project_title = "None (Void offset)"
            if params.project_id:
                proj = db.query(Project).filter(Project.id == params.project_id, Project.user_id == user.id).first()
                if proj:
                    project_title = f"[{proj.id}] {proj.title}"
                else:
                    # They hallucinated an ID or it doesn't belong to them
                    params.project_id = None

            # Create TimeLog
            new_log = TimeLog(
                user_id=user.id,
                session_id=active_session.id,
                project_id=params.project_id,
                duration_minutes=params.duration_minutes,
                description=params.description
            )
            db.add(new_log)
            
            if params.project_id and proj:
                proj.total_minutes_spent += params.duration_minutes
                
            db.commit()
            
            # Record action for Undo Engine
            action_log = ActionLog(
                user_id=user.id,
                tool_name="LOG_WORK",
                previous_state_json={},
                new_state_json={"timelog_id": new_log.id, "project_id": proj.id if params.project_id and proj else None, "duration_minutes": params.duration_minutes}
            )
            db.add(action_log)
            db.commit()

            await message.answer(
                f"✅ **Time Logged Successfully**\n"
                f"⏱ **Duration:** {params.duration_minutes} minutes\n"
                f"📂 **Project:** {project_title}\n"
                f"📝 **Note:** {params.description or 'No description'}",
                parse_mode="Markdown"
            )
    elif intent == IntentType.LOG_HABIT:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            active_habits = db.query(Habit).filter(Habit.user_id == user.id).all()
            if not active_habits:
                habits_text = "No habits found."
            else:
                habits_text = "\n".join([f"ID: {h.id} | Title: {h.title} | Target: {h.target_value}" for h in active_habits])
                
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            params, p_usage = extract_log_habit(message.text, provider, api_key, habits_text)
            log_tokens(message.from_user.id, p_usage)
            
            if not params or not params.habit_id:
                await message.answer("❌ Could not match a habit. Use `/new_habit` to create one first.")
                return
                
            habit = db.query(Habit).filter(Habit.id == params.habit_id, Habit.user_id == user.id).first()
            if habit:
                habit.current_value += params.amount_completed
                db.commit()
                
                # Record action
                action_log = ActionLog(
                    user_id=user.id,
                    tool_name="LOG_HABIT",
                    previous_state_json={"habit_id": habit.id, "amount_added": params.amount_completed},
                    new_state_json={"habit_id": habit.id, "current_value": habit.current_value}
                )
                db.add(action_log)
                db.commit()
                
                await message.answer(habit_updated_message(habit.title, habit.current_value, habit.target_value))
            else:
                await message.answer("❌ Invalid habit ID.")

    elif intent == IntentType.ADD_INBOX:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            params, p_usage = extract_inbox(message.text, provider, api_key)
            log_tokens(message.from_user.id, p_usage)
            if params and params.raw_content:
                new_inbox = Inbox(user_id=user.id, raw_text=params.raw_content)
                db.add(new_inbox)
                db.commit()
                await message.answer(inbox_saved_message(params.raw_content), parse_mode="Markdown")
            else:
                await message.answer("❌ Failed to parse inbox note.")

    elif intent == IntentType.UNDO:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            last_action = db.query(ActionLog).filter(ActionLog.user_id == user.id).order_by(ActionLog.id.desc()).first()
            
            if not last_action:
                await message.answer(nothing_to_undo_message())
                return
                
            if last_action.tool_name == "LOG_WORK":
                timelog_id = last_action.new_state_json.get("timelog_id")
                project_id = last_action.new_state_json.get("project_id")
                duration = last_action.new_state_json.get("duration_minutes", 0)
                
                t_log = db.query(TimeLog).filter(TimeLog.id == timelog_id).first()
                if t_log:
                    db.delete(t_log)
                if project_id:
                    proj = db.query(Project).filter(Project.id == project_id).first()
                    if proj:
                        proj.total_minutes_spent -= duration
                        
                db.delete(last_action)
                db.commit()
                await message.answer(undo_success_message("Time Log"))
                
            elif last_action.tool_name == "LOG_HABIT":
                habit_id = last_action.previous_state_json.get("habit_id")
                amount = last_action.previous_state_json.get("amount_added", 0)
                
                habit = db.query(Habit).filter(Habit.id == habit_id).first()
                if habit:
                    habit.current_value -= amount
                    
                db.delete(last_action)
                db.commit()
                await message.answer(undo_success_message("Habit progress"))
            else:
                await message.answer(undo_fail_message())

    elif intent == IntentType.SESSION_CONTROL:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        params, p_usage = extract_session_control(message.text, provider, api_key)
        log_tokens(message.from_user.id, p_usage)
        if params and params.action == "START":
            await cmd_start_session(message)
        elif params and params.action == "END":
            await cmd_end_session(message)
        else:
            await message.answer("❌ Could not determine session action.")
            
    elif intent == IntentType.CONFIG_REPORT:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        params, p_usage = extract_report_config(message.text, provider, api_key)
        log_tokens(message.from_user.id, p_usage)
        
        if params:
            with SessionLocal() as db:
                user = get_or_create_user(db, message.from_user.id)
                # Store it as JSON matching the layout: e.g. {"blocks": ["focus", "habits"], "style": "strict"}
                config_dict = {
                    "blocks": params.blocks,
                    "style": params.style
                }
                user.report_config = config_dict
                db.commit()
                
                await message.answer(f"✅ **Report Configuration Updated**\nStyle: `{params.style}`\nBlocks: `{', '.join(params.blocks)}`", parse_mode="Markdown")
        else:
            await message.answer("❌ Could not parse report configuration.")

    else:
        # Temporary debugging print so you can see what the AI decided
        await message.answer(f"*[DEBUG: Router fallback to {intent.value}]*\nI couldn't classify that clearly.", parse_mode="Markdown")

