"""
Logic for adding inbox items via AI intents.
@Architecture-Map: [HND-INTENT-ENT-INBOX]
"""

import html
from aiogram.types import Message
from src.db.models import Inbox
from src.ai.router import extract_inbox
from src.bot.handlers.utils import log_tokens

async def handle_add_inbox(message: Message, db, user, provider_name, api_key):
    extraction, tokens = await extract_inbox(message.text, provider_name, api_key)
    
    if tokens:
        log_tokens(db, message.from_user.id, tokens)
        
    if not extraction or not getattr(extraction, "raw_content", None):
        await message.answer("I could not determine what to save to your inbox.")
        return
        
    inbox_item = Inbox(user_id=user.id, raw_text=extraction.raw_content, status="pending")
    db.add(inbox_item)
    db.commit()
    
    safe_text = html.escape(extraction.raw_content)
    await message.answer(f"📥 <b>Saved to Inbox:</b>\n<i>{safe_text}</i>", parse_mode="HTML")
