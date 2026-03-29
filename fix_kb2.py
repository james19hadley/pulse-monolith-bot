import re

with open("src/bot/keyboards.py", "r", encoding='utf-8') as f:
    text = f.read()

text = re.sub(r',\n\s*\[\n\s*InlineKeyboardButton\(text="🎯 Manage Habits", callback_data="ui_habits_list"\)\n\s*\]', '', text)

with open("src/bot/keyboards.py", "w", encoding='utf-8') as f:
    f.write(text)

