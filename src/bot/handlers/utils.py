from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from src.db.models import User, TokenUsage

def get_or_create_user(db: DBSession, telegram_id: int) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def log_tokens(db: DBSession, telegram_id: int, usage_data: dict):
    if not usage_data: return
    try:
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
