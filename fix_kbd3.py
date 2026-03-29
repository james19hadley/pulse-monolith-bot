with open("src/bot/keyboards.py", "r", encoding='utf-8') as f:
    text = f.readlines()

def print_dups():
    lines = []
    in_dup = False
    dup_count = 0
    with open("src/bot/keyboards.py", "r", encoding='utf-8') as f:
        content = f.read()

import re
with open("src/bot/keyboards.py", "r", encoding='utf-8') as f:
    content = f.read()

# Fix duplicates
content = re.sub(r'(def get_reports_keyboard\(\) -> InlineKeyboardMarkup:.*?return InlineKeyboardMarkup\(inline_keyboard=kb\)\n+)(def get_reports_keyboard\(\) -> InlineKeyboardMarkup:.*?return InlineKeyboardMarkup\(inline_keyboard=kb\)\n+)', r'\1', content, flags=re.DOTALL)

with open("src/bot/keyboards.py", "w", encoding='utf-8') as f:
    f.write(content)
