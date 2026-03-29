import re

# keyboards.py
with open('src/bot/keyboards.py', 'r') as f:
    text = f.read()
text = text.replace('KeyboardButton(text="🎯 Habits"), ', '')
text = text.replace(', KeyboardButton(text="🎯 Habits")', '')
text = text.replace('KeyboardButton(text="🎯 Habits")', '')
with open('src/bot/keyboards.py', 'w') as f:
    f.write(text)

# states.py
with open('src/bot/states.py', 'r') as f:
    text = f.read()
text = re.sub(r'class HabitCreationForm\(StatesGroup\):.*?unit = State\(\)\n', '', text, flags=re.DOTALL)
with open('src/bot/states.py', 'w') as f:
    f.write(text)

# main.py
with open('src/main.py', 'r') as f:
    text = f.read()
text = re.sub(r'BotCommand\(command="habits", description="Active habits"\),?\s*', '', text)
text = re.sub(r'BotCommand\(command="new_habit", description="Create a habit"\),?\s*', '', text)
text = re.sub(r'BotCommand\(command="habit", description="Mark a habit"\),?\s*', '', text)
with open('src/main.py', 'w') as f:
    f.write(text)

# system_configs.py
with open('src/bot/handlers/settings/system_configs.py', 'r') as f:
    text = f.read()
text = text.replace("'focus', 'habits', 'inbox', 'void'", "'focus', 'projects', 'inbox', 'void'")
text = text.replace('"focus", "habits"', '"focus", "projects"')
with open('src/bot/handlers/settings/system_configs.py', 'w') as f:
    f.write(text)

# utils.py
with open('src/bot/handlers/utils.py', 'r') as f:
    text = f.read()
text = re.sub(r'def format_active_habits\(db: Session, user_id: int\) -> str:.*?return "\n"\.join\(lines\)', '', text, flags=re.DOTALL)
text = text.replace(', Habit', '')
with open('src/bot/handlers/utils.py', 'w') as f:
    f.write(text)

# texts.py
with open('src/bot/texts.py', 'r') as f:
    text = f.read()
text = text.replace('— `habits`', '')
text = text.replace('⚙️ Configure Report: Adjust how focus, habits, and tasks are presented.', '⚙️ Configure Report: Adjust how focus, projects, and tasks are presented.')
text = text.replace('habits', 'projects')
text = text.replace('📝 Log habit: /habit &lt;id/name&gt; [value]', '')
with open('src/bot/texts.py', 'w') as f:
    f.write(text)

print("done easy regexes")
