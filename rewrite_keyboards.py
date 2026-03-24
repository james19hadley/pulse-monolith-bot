import re

with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

# Replace main settings keyboard
old_kb_func = """def get_settings_keyboard() -> InlineKeyboardMarkup:
    \"\"\"Returns the main settings menu inline keyboard.\"\"\"
    kb = [
        [
            InlineKeyboardButton(text="🔑 API Keys", callback_data="settings_keys"),
            InlineKeyboardButton(text="🎭 Persona", callback_data="settings_persona")
        ],
        [
            InlineKeyboardButton(text="🌍 Timezone", callback_data="settings_timezone"),
            InlineKeyboardButton(text="📊 Reports", callback_data="settings_reports")
        ],
        [
            InlineKeyboardButton(text="⏱️ Catalyst", callback_data="settings_catalyst"),
            InlineKeyboardButton(text="🔁 Interval", callback_data="settings_interval")
        ],
        [
            InlineKeyboardButton(text="📢 Channel", callback_data="settings_channel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)"""

new_kb_func = """def get_settings_keyboard() -> InlineKeyboardMarkup:
    \"\"\"Returns the main settings menu inline keyboard.\"\"\"
    kb = [
        [
            InlineKeyboardButton(text="🔑 API Keys", callback_data="settings_keys"),
            InlineKeyboardButton(text="🎭 Persona", callback_data="settings_persona")
        ],
        [
            InlineKeyboardButton(text="🌍 Timezone", callback_data="settings_timezone"),
            InlineKeyboardButton(text="⏰ Report Time", callback_data="settings_cutoff")
        ],
        [
            InlineKeyboardButton(text="📊 Report Dest", callback_data="settings_reports"),
            InlineKeyboardButton(text="📢 Target Channel", callback_data="settings_channel")
        ],
        [
            InlineKeyboardButton(text="💓 Pulse Intervals", callback_data="settings_pulse")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_pulse_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏱️ Catalyst Limit", callback_data="settings_catalyst")
    builder.button(text="🔁 Repeat Interval", callback_data="settings_interval")
    builder.button(text="🔙 Back", callback_data="settings_main")
    builder.adjust(1, 1, 1)
    return builder.as_markup()

def get_cutoff_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="21:00", callback_data="set_cutoff_21:00")
    builder.button(text="22:00", callback_data="set_cutoff_22:00")
    builder.button(text="23:00", callback_data="set_cutoff_23:00")
    builder.button(text="00:00", callback_data="set_cutoff_00:00")
    builder.button(text="Custom Time", callback_data="set_cutoff_custom")
    builder.button(text="🔙 Back", callback_data="settings_main")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()"""

text = text.replace(old_kb_func, new_kb_func)

# Fix back buttons in intervals and channel to go to settings_pulse and settings_main
text = text.replace('builder.button(text="🔙 Back", callback_data="settings_main")', 'builder.button(text="🔙 Back", callback_data="settings_main_fallback")')

def fix_backs(m):
    return m.group(0).replace('settings_main_fallback', 'settings_pulse')

text = re.sub(r'def get_catalyst_keyboard.*?return builder.as_markup\(\)', fix_backs, text, flags=re.DOTALL)
text = re.sub(r'def get_interval_keyboard.*?return builder.as_markup\(\)', fix_backs, text, flags=re.DOTALL)
text = text.replace('settings_main_fallback', 'settings_main') # restore others

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)

