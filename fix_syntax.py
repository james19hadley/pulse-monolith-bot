import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

# For each function with bad formatting, we'll fix it manually using string replacements

text = text.replace('text = f"⏱️ <b>Catalyst Limit</b> (Minutes)\n\n<i>How much time should pass after the deadline before I notify you?</i>\n\n<b>Current:</b> <code>{current}</code>"', 
'text = f"""⏱️ <b>Catalyst Limit</b> (Minutes)\\n\\n<i>How much time should pass after the deadline before I notify you?</i>\\n\\n<b>Current:</b> <code>{current}</code>"""')

text = text.replace('text = f"⏱️ <b>Ping Interval</b> (Minutes)\n\n<i>How often should I ping you to remind you about the overdue habit?</i>\n\n<b>Current:</b> <code>{current}</code>"', 
'text = f"""⏱️ <b>Ping Interval</b> (Minutes)\\n\\n<i>How often should I ping you to remind you about the overdue habit?</i>\\n\\n<b>Current:</b> <code>{current}</code>"""')

text = text.replace('text = f"📣 <b>Target Channel</b>\n\nWhere should I post reports?\n\n<b>Current:</b> <code>{current}</code>"',
'text = f"""📣 <b>Target Channel</b>\\n\\nWhere should I post reports?\\n\\n<b>Current:</b> <code>{current}</code>"""')

text = text.replace('text = f"⏰ <b>Day Cutoff Time</b>\n\nAt what time should the day end for reporting purposes? (Format: HH:MM)\n\n<b>Current:</b> <code>{current}</code>"',
'text = f"""⏰ <b>Day Cutoff Time</b>\\n\\nAt what time should the day end for reporting purposes? (Format: HH:MM)\\n\\n<b>Current:</b> <code>{current}</code>"""')

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)
