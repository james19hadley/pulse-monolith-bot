import re
with open("src/bot/handlers/entities/menu.py", "r") as f:
    orig = f.read()

orig = orig.replace('get_entities_menu_keyboard', 'get_entities_main_keyboard')

with open("src/bot/handlers/entities/menu.py", "w") as f:
    f.write(orig)

