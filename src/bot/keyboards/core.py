from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.bot.texts import Buttons

def get_main_menu() -> ReplyKeyboardMarkup:
    # Uses true persistent text matching properly routed via decorators
    kb = [
        [
            KeyboardButton(text=Buttons.START_SESSION),
            KeyboardButton(text=Buttons.END_SESSION),
            KeyboardButton(text=Buttons.END_DAY)
        ],
        [
            KeyboardButton(text=Buttons.INBOX),
            KeyboardButton(text=Buttons.PROJECTS),
            KeyboardButton(text=Buttons.SETTINGS)
        ],
        [
            KeyboardButton(text=Buttons.HELP),
            KeyboardButton(text=Buttons.UNDO)
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)
