import re
import glob
import os

files_to_check = []
for root, dirs, files in os.walk("src"):
    for file in files:
        if file.endswith(".py") and file != "mig_s27.py":
            files_to_check.append(os.path.join(root, file))

for file in ["src/main.py"]:
    if file not in files_to_check and os.path.exists(file):
        files_to_check.append(file)

def clean_file(path_name):
    try:
        with open(path_name, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return
        
    original = content
    # Remove Habit from models import
    content = re.sub(r'[, ]*Habit\b', '', content)
    
    # In intent_entities.py: remove anything looking like Habit
    if 'intent_entities.py' in path_name:
        content = re.sub(r'for h in extraction\.habits:.*?(?=(?:if getattr|active_projects_text|#))', '', content, flags=re.DOTALL)
        content = re.sub(r'habits = db\.query\(Habit\).*?all\(\).*?(?=entities_list\.append)', '', content, flags=re.DOTALL)
        content = re.sub(r'existing = db\.query\(Habit\).*?\(msg\)', '', content, flags=re.DOTALL)
        
    # In commands.py
    if 'commands.py' in path_name:
        content = re.sub(r'@router\.message\(Command\("habits?"\)\).*?(?=@router|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'async def cmd_habits?.*?Habit.*?$', '', content, flags=re.DOTALL)
        
    # In menu.py
    if 'menu.py' in path_name:
        content = re.sub(r'habits = db\.query\(Habit\).*?all\(\)', '', content)

    # In core.py
    if 'core.py' in path_name:
        content = re.sub(r'hab = db\.query\(Habit\).*?deleted\."\)', '', content, flags=re.DOTALL)

    # In projects.py
    if 'projects.py' in path_name:
        pass
        
    # main.py
    if 'main.py' in path_name:
        content = re.sub(r'BotCommand\(command="habit".*?\),?\n?', '', content)

    # system_configs.py
    if 'system_configs.py' in path_name:
        content = content.replace('about the overdue habit?', 'about the overdue project?')
        content = content.replace('if the habit remains', 'if the project remains')

    # keyboards.py
    if 'keyboards.py' in path_name:
        content = re.sub(r'kb\.append\(\[InlineKeyboardButton\(text="➕ New Habit".*?\n?', '', content)

    if original != content:
        with open(path_name, "w", encoding="utf-8") as f:
            f.write(content)

for fn in files_to_check:
    clean_file(fn)

