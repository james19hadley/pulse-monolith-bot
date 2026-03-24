import sys

with open('src/main.py', 'r') as f:
    orig = f.read()

bad_chunk = """async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    import logging
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Suppress aiogram's default event log which prints full messages
logging.getLogger("aiogram.event").setLevel(logging.WARNING)

class SafeLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Avoid crashing on missing user/message
        try:
            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else "Unknown"
                text = event.message.text
                if text:
                    if text.startswith('/'):
                        logging.info(f"User {user_id} triggered command: {text.split()[0]}")
                    else:
                        logging.info(f"User {user_id} sent text message (length: {len(text)})")
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
                data_cb = event.callback_query.data
                logging.info(f"User {user_id} tapped inline button: {data_cb}")
        except Exception:
            pass
            
        return await handler(event, data)

dp = Dispatcher()
dp.update.outer_middleware(SafeLoggingMiddleware())

    
    # Register handlers
    for router in routers:"""

good_chunk = """from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Suppress aiogram's default event log which prints full messages
logging.getLogger("aiogram.event").setLevel(logging.WARNING)

class SafeLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Avoid crashing on missing user/message
        try:
            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else "Unknown"
                text = event.message.text
                if text:
                    if text.startswith('/'):
                        logging.info(f"User {user_id} triggered command: {text.split()[0]}")
                    else:
                        logging.info(f"User {user_id} sent text message (length: {len(text)})")
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
                data_cb = event.callback_query.data
                logging.info(f"User {user_id} tapped inline button: {data_cb}")
        except Exception:
            pass
            
        return await handler(event, data)

async def main():
    # Initialize Bot and Dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.update.outer_middleware(SafeLoggingMiddleware())

    # Register handlers
    for router in routers:"""

if bad_chunk in orig:
    new_code = orig.replace(bad_chunk, good_chunk)
    with open('src/main.py', 'w') as f:
        f.write(new_code)
    print("Fixed!")
else:
    print("Could not find bad chunk!")

