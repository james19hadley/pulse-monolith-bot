from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Returns the persistent bottom keyboard menu."""
    kb = [
        [
            KeyboardButton(text="🟢 Start Session"),
            KeyboardButton(text="🛑 End Session")
        ],
        [
            KeyboardButton(text="📥 Inbox"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)

def get_providers_keyboard() -> InlineKeyboardMarkup:
    """Returns an inline keyboard with AI providers for the Add Key flow."""
    kb = [
        [
            InlineKeyboardButton(text="Google (Gemini)", callback_data="provider_google"),
            InlineKeyboardButton(text="OpenAI", callback_data="provider_openai"),
            InlineKeyboardButton(text="Anthropic", callback_data="provider_anthropic")
        ],
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_fsm")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
