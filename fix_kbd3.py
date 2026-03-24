import re

with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

# Replace "Report Dest" with "Report"
text = text.replace('text="📊 Report Dest"', 'text="📊 Report"')

# In get_reports_keyboard, replace the buttons 
def_to_replace = """def get_reports_keyboard() -> InlineKeyboardMarkup:
    \"\"\"Keyboard to select report destination.\"\"\"
    kb = [
        [
            InlineKeyboardButton(text="📩 Send to DM", callback_data="set_report_dm"),
            InlineKeyboardButton(text="📢 Send to Channel", callback_data="set_report_channel")
        ],
        [InlineKeyboardButton(text="❌ Disable Reports", callback_data="set_report_none")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)"""

replacement_def = """def get_reports_keyboard() -> InlineKeyboardMarkup:
    \"\"\"Keyboard to select report destination and format.\"\"\"
    kb = [
        [
            InlineKeyboardButton(text="📩 Send to DM", callback_data="set_report_dm"),
            InlineKeyboardButton(text="📢 Send to Channel", callback_data="set_report_channel")
        ],
        [
            InlineKeyboardButton(text="❌ Disable Reports", callback_data="set_report_none"),
            InlineKeyboardButton(text="🧪 Test Report", callback_data="settings_test_report")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)"""

if def_to_replace in text:
    text = text.replace(def_to_replace, replacement_def)
else:
    # try regex
    text = re.sub(r'def get_reports_keyboard\(\).*?return InlineKeyboardMarkup\(inline_keyboard=kb\)', replacement_def, text, flags=re.DOTALL)

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)

