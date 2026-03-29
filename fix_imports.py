import urllib
import glob

files = glob.glob('src/bot/handlers/intents/*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'get_main_menu' not in content:
        content = "from src.bot.keyboards import get_main_menu\n" + content
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
