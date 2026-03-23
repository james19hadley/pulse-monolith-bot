import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import TELEGRAM_BOT_TOKEN
from src.bot.handlers import router
from src.scheduler.jobs import catalyst_heartbeat, stale_session_killer, daily_accountability_job

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
    
    # Setup Telegram Bot Commands Menu
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="help", description="Show all manual commands"),
        BotCommand(command="start_session", description="Begin tracking session"),
        BotCommand(command="end_session", description="Stop tracking session"),
        BotCommand(command="log", description="Quick log: /log <min> [desc]"),
        BotCommand(command="habit", description="Mark habit: /habit <id/name>"),
        BotCommand(command="inbox", description="Save thought: /inbox <text>"),
        BotCommand(command="projects", description="List active projects"),
        BotCommand(command="new_project", description="Create: /new_project <name>"),
        BotCommand(command="new_habit", description="Create: /new_habit <name>"),
        BotCommand(command="settings", description="View or change configs"),
        BotCommand(command="stats", description="Show API usage tokens/cost"),
        BotCommand(command="test_report", description="Force generate daily report"),
    ]
    await bot.set_my_commands(commands)
    
    print("⬛ Pulse Monolith bot is starting (Long Polling)...")
    
    # Initialize background scheduler
    scheduler = AsyncIOScheduler()
    # Runs the heartbeat every 5 minutes to allow for custom user thresholds
    scheduler.add_job(catalyst_heartbeat, 'interval', minutes=5, args=[bot])
    scheduler.add_job(stale_session_killer, 'interval', hours=1, args=[bot])
    scheduler.add_job(daily_accountability_job, 'cron', minute=0, args=[bot]) # Run at the top of every hour to check for 
    scheduler.start()
    
    # Drop any pending updates before starting (so it doesn't process old missed messages)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⬛ Pulse Monolith shutdown complete.")
