import datetime
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from src.db.repo import SessionLocal
from src.db.models import User, Session, Project, TimeLog
from src.core.constants import IntentType
from src.bot.views import (
    welcome_message, 
    session_started_message, 
    session_already_active_message,
    no_active_session_message,
    session_ended_message,
    project_created_message,
    project_list_message
)
from src.core.security import encrypt_key, decrypt_key
from src.ai.router import get_intent, extract_log_work

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
    
    intent = get_intent(message.text, provider, api_key)
    
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
            params = extract_log_work(message.text, provider, api_key, projects_text)

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

            await message.answer(
                f"✅ **Time Logged Successfully**\n"
                f"⏱ **Duration:** {params.duration_minutes} minutes\n"
                f"📂 **Project:** {project_title}\n"
                f"📝 **Note:** {params.description or 'No description'}",
                parse_mode="Markdown"
            )
    else:
        # Temporary debugging print so you can see what the AI decided
        await message.answer(f"*[DEBUG: Router classified intent as {intent.value}]*", parse_mode="Markdown")

