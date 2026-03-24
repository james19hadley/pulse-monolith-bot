with open("src/bot/views.py", "r") as f:
    text = f.read()

text = text.replace('умеешь\\"</i>               "', 'умеешь\\"</i>\\n"')
text = text.replace('Python\\"</i>   "', 'Python\\"</i>\\n"')

with open("src/bot/views.py", "w") as f:
    f.write(text)
