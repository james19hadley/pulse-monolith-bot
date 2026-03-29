import re

with open("src/bot/keyboards.py", "r", encoding='utf-8') as f:
    text = f.read()

# Fix any weird Back characters (e.g. ) using regex
text = re.sub(r'text=".*?🔙 Back"', 'text="🔙 Back"', text)

with open("src/bot/keyboards.py", "w", encoding='utf-8') as f:
    f.write(text)

