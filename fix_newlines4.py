with open("src/bot/views.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Расскажи о том что ты умеешь" in line:
        lines[i] = '    msg += "• <i>\\"Расскажи о том что ты умеешь\\"</i>\\n"\n'
    elif "Create a new project for learning Python" in line:
        lines[i] = '    msg += "• <i>\\"Create a new project for learning Python\\"</i>\\n"\n'

with open("src/bot/views.py", "w") as f:
    f.writelines(lines)

