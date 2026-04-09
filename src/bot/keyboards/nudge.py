"""
Keyboard for proactive session nudging.

@Architecture-Map: [UI-KEY-NUDGE]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.texts import Buttons

def get_nudge_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text=Buttons.NUDGE_WORKING, callback_data="nudge_working"),
            InlineKeyboardButton(text=Buttons.NUDGE_FINISH, callback_data="nudge_finish")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
