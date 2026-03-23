import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import TELEGRAM_BOT_TOKEN
from src.bot.handlers import router
from src.scheduler.jobs import catalyst_heartbeat

# Setup logging to both console and a persistent file (bot.log)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(router)
    
    print("⬛ Pulse Monolith bot is starting (Long Polling)...")
    
    # Initialize background scheduler
    scheduler = AsyncIOScheduler()
    # Runs the heartbeat every 5 minutes to allow for custom user thresholds
    scheduler.add_job(catalyst_heartbeat, 'interval', minutes=5, args=[bot])
    scheduler.start()
    
    # Drop any pending updates before starting (so it doesn't process old missed messages)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⬛ Pulse Monolith shutdown complete.")
