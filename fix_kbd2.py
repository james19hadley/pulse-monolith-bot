with open("src/bot/keyboards.py", "a") as f:
    f.write('''
def get_api_keys_manage_keyboard() -> InlineKeyboardMarkup:
    """Manage API Keys Main Menu."""
    kb = [
        [InlineKeyboardButton(text="➕ Add New Key", callback_data="settings_add_key")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
''')
