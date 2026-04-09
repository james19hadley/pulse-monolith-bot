"""
The root celery task declarations module which imports core jobs.

@Architecture-Map: [JOB-CELERY-MOD]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import os
import asyncio
from celery import shared_task
from aiogram import Bot
from src.db.repo import SessionLocal
from src.db.models import User
from src.bot.views import catalyst_ping_message
from datetime import datetime, timedelta

# Create a global bot instance for the worker process
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    # Just a placeholder so it doesn't crash on import if env is missing
    bot = None
else:
    bot = Bot(token=BOT_TOKEN)

# We need an async helper to run aiogram logic inside Celery's synchronous threads
def run_async(coro):
    # Celery workers use synchronous execution by default.
    # To run an async aiogram network call, we create an event loop, run the task, and close it.
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@shared_task(name="send_catalyst_ping")
def send_catalyst_ping(telegram_id: int, hours_idle: float):
    """
    Background Task: Sends the inactivity warning directly to the user.
    """
    if bot is None:
        print("BOT_TOKEN is not configured for worker.")
        return False
        
    try:
        msg_text = catalyst_ping_message(hours_idle)
        run_async(bot.send_message(chat_id=telegram_id, text=msg_text))
        return True
    except Exception as e:
        print(f"Failed to send ping to {telegram_id} via Celery: {e}")
        return False
