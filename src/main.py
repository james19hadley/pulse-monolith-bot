"""
Main entry point for the FastAPI webhook server and Telegram Bot polling fallback.

@Architecture-Map: [APP-MAIN-ENTRY]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.core.config import TELEGRAM_BOT_TOKEN, WEBHOOK_SECRET, WEBHOOK_DOMAIN, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from src.bot import routers
from src.admin_dashboard import dashboard_handler, logs_handler

# Setup logging to both console and a persistent file (bot.log)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Suppress aiogram's default event log which prints full messages
logging.getLogger("aiogram.event").setLevel(logging.WARNING)

class SafeLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Logging Phase
        try:
            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else "Unknown"
                text = event.message.text
                if text:
                    if text.startswith('/'):
                        logging.info(f"User {user_id} triggered command: {text.split()[0]}")
                    else:
                        logging.info(f"User {user_id} sent text message (length: {len(text)})")
            elif getattr(event, "callback_query", None):
                user_id = event.callback_query.from_user.id
                data_cb = event.callback_query.data
                logging.info(f"User {user_id} tapped inline button: {data_cb}")
        except Exception as e:
            logging.error(f"Error in SafeLoggingMiddleware: {e}")
            
        # Exception Handling Phase for inner routes
        try:
            return await handler(event, data)
        except Exception as e:
            logging.error(f"Global exception caught: {e}", exc_info=True)
            if event.message:
                try:
                    await event.message.answer("⚠️ Простите, на сервере произошла ошибка. Пожалуйста, обратитесь позднее.")
                except Exception:
                    pass
            elif getattr(event, "callback_query", None):
                try:
                    await event.callback_query.message.answer("⚠️ Простите, на сервере произошла ошибка. Пожалуйста, обратитесь позднее.")
                except Exception:
                    pass

async def main():
    logging.info("🚀 Pulse Monolith Bot is booting up...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.update.outer_middleware(SafeLoggingMiddleware())
    
    # Register handlers
    logging.info(f"Registering {len(routers)} main routers...")
    for router in routers:
        dp.include_router(router)
    
    # Setup Telegram Bot Commands Menu
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="help", description="Show all manual commands"),
        BotCommand(command="start_session", description="Begin tracking session"),
        BotCommand(command="end_session", description="Stop tracking session"),
        BotCommand(command="log", description="Quick log: /log <min> [desc]"),
                BotCommand(command="inbox", description="View/save thoughts"),
        BotCommand(command="clear_inbox", description="Empty the inbox"),
        BotCommand(command="projects", description="List active projects"),
        BotCommand(command="new_project", description="Create: /new_project <name>"),
        BotCommand(command="new_habit", description="Create: /new_habit <name>"),
        BotCommand(command="settings", description="View or change configs"),
        BotCommand(command="report_config", description="Configure daily reports UI"),
        BotCommand(command="stats", description="Show API usage tokens/cost"),
        BotCommand(command="test_report", description="Force generate daily report"),
        BotCommand(command="add_key", description="Add new API key"),
        BotCommand(command="my_key", description="Check key status"),
        BotCommand(command="use_key", description="Switch active AI provider"),
        BotCommand(command="delete_key", description="Delete API key"),
    ]
    await bot.set_my_commands(commands)
    
    from src.db.repo import init_db
    init_db()
    
    # Drop any pending updates before starting
    await bot.delete_webhook(drop_pending_updates=True)
    
    if WEBHOOK_DOMAIN:
        logging.info(f"Setting up Webhook mode on {WEBHOOK_DOMAIN}...")
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            secret_token=WEBHOOK_SECRET,
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        app.router.add_get('/admin/dashboard', dashboard_handler)
        app.router.add_get('/admin/logs', logs_handler)        
        webhook_url = f"https://{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"
        logging.info(f"Setting up Webhook mode on {webhook_url}...")
        
        # Log webhook setup details
        logging.info(f"Webhook URL: {webhook_url}")
        logging.info(f"Webhook Host: {WEBAPP_HOST}, Port: {WEBAPP_PORT}")
        
        # Explicitly ask Telegram to send all update types we setup
        await bot.set_webhook(
            webhook_url,
            secret_token=WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query", "inline_query", "my_chat_member"]
        )
        logging.info(f"✅ Webhook successfully set to {webhook_url}")
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
        await site.start()
        
        while True:
            await asyncio.sleep(3600)
    else:
        print("⬛ Pulse Monolith bot is starting (Long Polling)...")
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⬛ Pulse Monolith shutdown complete.")
