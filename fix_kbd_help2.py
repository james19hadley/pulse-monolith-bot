with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

text = text.replace('KeyboardButton(text="❓ Help"),\n            KeyboardButton(text="❓ Help")', 'KeyboardButton(text="❓ Help")')
with open("src/bot/keyboards.py", "w") as f:
    f.write(text)
