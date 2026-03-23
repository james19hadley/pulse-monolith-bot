import asyncio
import logging
from aiogram import Bot, Dispatcher

from src.core.config import TELEGRAM_BOT_TOKEN
from src.bot.handlers import router

# Setup basic logging to see aiogram output in the terminal
logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(router)
    
    print("⬛ Pulse Monolith bot is starting (Long Polling)...")
    
    # Drop any pending updates before starting (so it doesn't process old missed messages)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⬛ Pulse Monolith shutdown complete.")
