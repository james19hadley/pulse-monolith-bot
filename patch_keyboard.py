import re
with open("src/bot/keyboards.py", "r") as f:
    orig = f.read()

s1 = """        [
            InlineKeyboardButton(text="📦 Archive", callback_data=f"ui_proj_arch_{proj_id}")
        ],"""
r1 = """        [
            InlineKeyboardButton(text="📦 Archive", callback_data=f"ui_proj_arch_{proj_id}"),
            InlineKeyboardButton(text="🗑 Delete", callback_data=f"ui_proj_delete_{proj_id}")
        ],"""

orig = orig.replace(s1, r1)

with open("src/bot/keyboards.py", "w") as f:
    f.write(orig)

