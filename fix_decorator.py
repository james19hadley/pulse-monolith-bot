with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

text = text.replace('@router.callback_query(F.data.startswith("settings_"))', '@router.callback_query(F.data.in_({"settings_keys", "settings_add_key", "settings_persona", "settings_timezone", "settings_reports", "settings_back", "settings_main"}))')

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

