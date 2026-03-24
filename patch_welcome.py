import re

with open("src/bot/views.py", "r") as f:
    text = f.read()

# Modify the AI comment in settings_keys
with open("src/bot/handlers/settings_keys.py", "r") as f:
    settings_text = f.read()
settings_text = settings_text.replace('ai_comment = "<i>(AI Summary would appear here based on your actual daily logs and stats)</i>"', 'ai_comment = "(AI Summary would appear here based on your actual daily logs and stats)"')
with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(settings_text)

