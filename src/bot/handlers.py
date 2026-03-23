import datetime
from aiogram import Router
from aiogram.filters import Command
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
        get_or_create_user(db, message.from_user.id)
    await message.answer(welcome_message())

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
        duration_minutes = int(duration.total_seconds() / 60)
        
        db.commit()
        
    await message.answer(session_ended_message(duration_minutes))
