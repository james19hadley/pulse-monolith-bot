with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

import re
# Clean up duplicate imports from my repeated script
text = re.sub(r'from src\.bot\.keyboards import .*?\n', 'from src.bot.keyboards import get_providers_keyboard, get_settings_keyboard, get_persona_keyboard, get_reports_keyboard, get_timezone_keyboard, get_back_settings_keyboard, get_api_keys_manage_keyboard, get_catalyst_keyboard, get_interval_keyboard, get_channel_keyboard, get_pulse_menu_keyboard, get_cutoff_keyboard\n', text)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)
