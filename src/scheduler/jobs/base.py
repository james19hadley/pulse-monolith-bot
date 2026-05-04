"""
Base configuration for background jobs.
@Architecture-Map: [JOB-BASE]
"""
import os
from aiogram import Bot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    bot = None
else:
    bot = Bot(token=BOT_TOKEN)
