import asyncio
import logging
from aiogram import Bot, Dispatcher


from src.core.config import TELEGRAM_BOT_TOKEN
from src.bot import routers


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
    for router in routers:
        dp.include_router(router)
    
    # Setup Telegram Bot Commands Menu
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="help", description="Show all manual commands"),
        BotCommand(command="start_session", description="Begin tracking session"),
        BotCommand(command="end_session", description="Stop tracking session"),
        BotCommand(command="log", description="Quick log: /log <min> [desc]"),
        BotCommand(command="habit", description="Mark habit: /habit <id/name>"),
        BotCommand(command="inbox", description="View/save thoughts"),
        BotCommand(command="clear_inbox", description="Empty the inbox"),
        BotCommand(command="projects", description="List active projects"),
        BotCommand(command="new_project", description="Create: /new_project <name>"),
        BotCommand(command="new_habit", description="Create: /new_habit <name>"),
        BotCommand(command="settings", description="View or change configs"),
        BotCommand(command="stats", description="Show API usage tokens/cost"),
        BotCommand(command="test_report", description="Force generate daily report"),
        BotCommand(command="add_key", description="Add new API key"),
        BotCommand(command="my_key", description="Check key status"),
        BotCommand(command="use_key", description="Switch active AI provider"),
        BotCommand(command="delete_key", description="Delete API key"),
    ]
    await bot.set_my_commands(commands)
    
    print("⬛ Pulse Monolith bot is starting (Long Polling)...")
    
    
    # Drop any pending updates before starting (so it doesn't process old missed messages)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⬛ Pulse Monolith shutdown complete.")
