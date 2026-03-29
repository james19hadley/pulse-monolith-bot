import os
file_path = "src/bot/handlers/intents/intent_log_work.py"
with open(file_path, "r") as f:
    content = f.read()

# Remove inline undo
if 'keyboard = InlineKeyboardMarkup(inline_keyboard=[[\n        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_work_{log_entry.id}")\n    ]])' in content:
    content = content.replace(
        'keyboard = InlineKeyboardMarkup(inline_keyboard=[[\n        InlineKeyboardButton(text="↩️ Undo", callback_data=f"undo_work_{log_entry.id}")\n    ]])',
        'from src.bot.keyboards import get_main_menu\n    keyboard = get_main_menu()'
    )

with open(file_path, "w") as f:
    f.write(content)
print("done")
