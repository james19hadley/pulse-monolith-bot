import re

with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

def inject_kb():
    if "settings_catalyst" in text:
        return text
    
    return re.sub(
        r'InlineKeyboardButton\(text="📊 Reports", callback_data="settings_reports"\)\n\s+\]\n\s+\]',
        'InlineKeyboardButton(text="📊 Reports", callback_data="settings_reports")\n        ],\n        [\n            InlineKeyboardButton(text="⏱️ Catalyst", callback_data="settings_catalyst"),\n            InlineKeyboardButton(text="🔁 Interval", callback_data="settings_interval")\n        ],\n        [\n            InlineKeyboardButton(text="📢 Channel", callback_data="settings_channel")\n        ]\n    ]',
        text
    )

new_text = inject_kb()

with open("src/bot/keyboards.py", "w") as f:
    f.write(new_text)

