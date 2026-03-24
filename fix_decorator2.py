with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

text = text.replace('"settings_timezone", "settings_reports", "settings_back", "settings_main"!', '"settings_timezone", "settings_reports", "settings_back", "settings_main", "settings_pulse", "settings_cutoff"}))')

# Oops, the previous regex was for `}))`, let me do exact replace
text = text.replace('{"settings_keys", "settings_add_key", "settings_persona", "settings_timezone", "settings_reports", "settings_back", "settings_main"}', '{"settings_keys", "settings_add_key", "settings_persona", "settings_timezone", "settings_reports", "settings_back", "settings_main", "settings_pulse", "settings_cutoff"}')

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

