with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

pulse_bad = '''    text = (
        "💓 <b>Pulse Intervals</b>                

"
        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.                "
        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue. 

"
        f"<b>Current Settings:</b>                "
        f"Catalyst: <code>{catalyst}</code> min   "
        f"Ping: <code>{interval}</code> min"           )'''

pulse_good = '''    text = (
        "💓 <b>Pulse Intervals</b>\\n\\n"
        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.\\n"
        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue.\\n\\n"
        f"<b>Current Settings:</b>\\n"
        f"Catalyst: <code>{catalyst}</code> min\\n"
        f"Ping: <code>{interval}</code> min"
    )'''

# Instead of regex, let's just do pure substring replacement of the bad string block for settings_pulse
start_str = '    text = (\n        "💓 <b>Pulse Intervals</b>'
end_str = '        f"Ping: <code>{interval}</code> min"           )'

idx1 = text.find(start_str)
idx2 = text.find(end_str)

if idx1 != -1 and idx2 != -1:
    text = text[:idx1] + pulse_good + text[idx2 + len(end_str):]


# And the other bad strings

text = text.replace('text = f"⏱️ <b>Catalyst Limit</b> (Minutes)\n\n<i>How much time should pass after the deadline before I notify you?</i>\n\n<b>Current:</b> <code>{current}</code>"', 
'text = f"⏱️ <b>Catalyst Limit</b> (Minutes)\\n\\n<i>How much time should pass after the deadline before I notify you?</i>\\n\\n<b>Current:</b> <code>{current}</code>"')

text = text.replace('text = f"⏱️ <b>Ping Interval</b> (Minutes)\n\n<i>How often should I ping you to remind you about the overdue habit?</i>\n\n<b>Current:</b> <code>{current}</code>"', 
'text = f"⏱️ <b>Ping Interval</b> (Minutes)\\n\\n<i>How often should I ping you to remind you about the overdue habit?</i>\\n\\n<b>Current:</b> <code>{current}</code>"')

text = text.replace('text = f"📣 <b>Target Channel</b>\n\nWhere should I post reports?\n\n<b>Current:</b> <code>{current}</code>"',
'text = f"📣 <b>Target Channel</b>\\n\\nWhere should I post reports?\\n\\n<b>Current:</b> <code>{current}</code>"')

text = text.replace('text = f"⏰ <b>Day Cutoff Time</b>\n\nAt what time should the day end for reporting purposes? (Format: HH:MM)\n\n<b>Current:</b> <code>{current}</code>"',
'text = f"⏰ <b>Day Cutoff Time</b>\\n\\nAt what time should the day end for reporting purposes? (Format: HH:MM)\\n\\n<b>Current:</b> <code>{current}</code>"')

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

