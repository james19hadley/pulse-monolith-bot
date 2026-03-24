with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

text = text.replace('from aiogram.utils.keyboard import InlineKeyboardBuilder\nfrom aiogram.utils.keyboard import InlineKeyboardBuilder', 'from aiogram.utils.keyboard import InlineKeyboardBuilder')

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)
