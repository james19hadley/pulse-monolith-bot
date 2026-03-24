import re

with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

# Replace the get_main_menu function to include the Help button
old_menu = """def get_main_menu() -> ReplyKeyboardMarkup:
    \"\"\"Returns the persistent bottom keyboard menu.\"\"\"
    kb = [
        [
            KeyboardButton(text=" 🟢 Start Session"),
            KeyboardButton(text=" 🛑 End Session")
        ],
        [
            KeyboardButton(text=" 📥 Inbox"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)"""

new_menu = """def get_main_menu() -> ReplyKeyboardMarkup:
    \"\"\"Returns the persistent bottom keyboard menu.\"\"\"
    kb = [
        [
            KeyboardButton(text=" 🟢 Start Session"),
            KeyboardButton(text=" 🛑 End Session")
        ],
        [
            KeyboardButton(text=" 📥 Inbox"),
            KeyboardButton(text="⚙️ Settings"),
            KeyboardButton(text="❓ Help")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)"""

if old_menu in text:
    text = text.replace(old_menu, new_menu)
else:
    # Fallback if there are minor differences
    text = text.replace('KeyboardButton(text="⚙️ Settings")', 'KeyboardButton(text="⚙️ Settings"),\n            KeyboardButton(text="❓ Help")')

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)

