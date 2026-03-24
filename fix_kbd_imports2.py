with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

text = text.replace('from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton', 'from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton\\nfrom aiogram.utils.keyboard import InlineKeyboardBuilder')

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)
