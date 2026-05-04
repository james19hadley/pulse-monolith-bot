"""
Handling Inbox intents (e.g. Clearing Inbox).

@Architecture-Map: [HND-INTENT-INBOX]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import Message
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user

async def _handle_clear_inbox(message: Message, db, user, provider_name, api_key):
    from src.db.models import Inbox
    cleared = db.query(Inbox).filter(Inbox.user_id == user.id, Inbox.status == "pending").update({"status": "cleared"})
    db.commit()
    await message.answer(f"🧹 Inbox cleared. Removed {cleared} items.")
