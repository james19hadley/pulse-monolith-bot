"""
Basic UI inline keyboards (Pagination loops, Yes/No, Back, and Home).

@Architecture-Map: [UI-KEY-CORE]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.bot.texts import Buttons

def get_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text=Buttons.START_SESSION),
            KeyboardButton(text=Buttons.END_SESSION),
            KeyboardButton(text=Buttons.END_DAY)
        ],
        [
            KeyboardButton(text=Buttons.INBOX),
            KeyboardButton(text=Buttons.TASKS),
            KeyboardButton(text=Buttons.PROJECTS)
        ],
        [
            KeyboardButton(text=Buttons.STATS),
            KeyboardButton(text=Buttons.SETTINGS),
            KeyboardButton(text=Buttons.UNDO)
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)
