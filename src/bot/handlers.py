import datetime
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.orm import Session as DBSession

from src.db.repo import SessionLocal
from src.db.models import User, Session
from src.bot.views import (
    welcome_message, 
    session_started_message, 
    session_already_active_message,
    no_active_session_message,
    session_ended_message
)
from src.core.security import encrypt_key, decrypt_key
from src.ai.router import get_intent

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
        duration_minutes = int(duration.total_seconds() / 60)
        # If it's less than a minute, show 1 minute so the user knows they tracked *something*
        if duration_minutes == 0 and duration.total_seconds() > 0:
            duration_minutes = 1
            
        db.commit()
        
    await message.answer(session_ended_message(duration_minutes))

@router.message(Command("set_key"))
async def cmd_set_key(message: Message, command: CommandObject):
    """Saves the user's personal API key securely to the database."""
    if not command.args:
        await message.answer("Usage: /set_key <your_api_key>")
        return
        
    api_key = command.args.strip()
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        # Encrypt the key before saving it to the database
        user.api_key_encrypted = encrypt_key(api_key)
        user.llm_provider = "google" # Defaulting to google since you requested Gemini
        db.commit()
        

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
    
    # Temporary debugging print so you can see what the AI decided
    await message.answer(f"*[DEBUG: Router classified intent as {intent}]*", parse_mode="Markdown")
    await message.answer("API Key successfully encrypted and secured in the database. I will use it for processing protocols.")

