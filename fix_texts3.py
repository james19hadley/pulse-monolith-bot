with open("src/bot/handlers/settings_keys.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False

for i, line in enumerate(lines):
    if line.startswith('    text = ('):
        if i + 1 < len(lines) and 'Pulse Intervals' in lines[i+1]:
            skip = True
            new_lines.append('    text = (\n')
            new_lines.append('        "💓 <b>Pulse Intervals</b>\\n\\n"\n')
            new_lines.append('        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.\\n"\n')
            new_lines.append('        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue.\\n\\n"\n')
            new_lines.append('        f"<b>Current Settings:</b>\\n"\n')
            new_lines.append('        f"Catalyst: <code>{catalyst}</code> min\\n"\n')
            new_lines.append('        f"Ping: <code>{interval}</code> min"\n')
            new_lines.append('    )\n')
            continue
    if skip:
        if line.strip() == ')':
            skip = False
        continue
    new_lines.append(line)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.writelines(new_lines)
