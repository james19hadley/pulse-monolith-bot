import re

with open("src/bot/views.py", "r") as f:
    text = f.read()

text = re.sub(r'\"Расскажи о том что ты умеешь\\"</i>\s*"', '"Расскажи о том что ты умеешь\\"</i>\\n"', text)
text = re.sub(r'\"Create a new project for learning Python\\"</i>\s*"', '"Create a new project for learning Python\\"</i>\\n"', text)

with open("src/bot/views.py", "w") as f:
    f.write(text)

