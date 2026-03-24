with open("src/bot/keyboards.py", "r") as f:
    text = f.read()

if "from aiogram.utils.keyboard import InlineKeyboardBuilder" not in text:
    text = text.replace("from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton", "from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton\\nfrom aiogram.utils.keyboard import InlineKeyboardBuilder")

with open("src/bot/keyboards.py", "w") as f:
    f.write(text)
