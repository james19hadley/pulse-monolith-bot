import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

pulse_good = '''    text = (
        "💓 <b>Pulse Intervals</b>\\n\\n"
        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.\\n"
        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue.\\n\\n"
        f"<b>Current Settings:</b>\\n"
        f"Catalyst: <code>{catalyst}</code> min\\n"
        f"Ping: <code>{interval}</code> min"
    )
'''

pattern = r'text \= \(\n\s*"💓 <b>Pulse Intervals</b>.*?\)'

text = re.sub(pattern, pulse_good.strip(), text, flags=re.DOTALL)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

