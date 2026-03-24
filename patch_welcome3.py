import re

with open("src/bot/views.py", "r") as f:
    text = f.read()

text = re.sub(
    r'msg \+= "• <i>\\"Create a new project for learning Python\\"</i>\\n"',
    'msg += "• <i>\\"Расскажи о том что ты умеешь\\"</i>\\n"\n    msg += "• <i>\\"Create a new project for learning Python\\"</i>\\n"',
    text
)

with open("src/bot/views.py", "w") as f:
    f.write(text)

