import re
import os

def repl(file, rules, is_regex=False):
    if not os.path.exists(file): return
    try:
        with open(file, 'r') as f:
            c = f.read()
        for pat, rep in rules:
            if is_regex:
                c = re.sub(pat, rep, c, flags=re.DOTALL)
            else:
                c = c.replace(pat, rep)
        with open(file, 'w') as f:
            f.write(c)
    except Exception as e:
        print(f"Error {file}: {e}")

# entities/commands.py
repl('src/bot/handlers/entities/commands.py', [
    ('@router.message(Command("habits"))', ''),
    ('async def cmd_habits(', 'async def cmd_habits_removed('),
    ('@router.message(Command("new_habit"))', ''),
    ('async def cmd_new_habit(', 'async def cmd_new_habit_removed('),
])

# Just completely remove those functions using regex
with open('src/bot/handlers/entities/commands.py', 'r') as f:
    text = f.read()
text = re.sub(r'@router\.message\(Command\("habits"\)\).*?sys_views\.msg_list_active_habits\(message, habits\)', '', text, flags=re.DOTALL)
text = re.sub(r'async def cmd_habits_removed\(.*?sys_views\.msg_list_active_habits\(message, habits\)', '', text, flags=re.DOTALL)
text = re.sub(r'@router\.message\(Command\("new_habit"\)\).*?await state\.set_state.*?HabitCreationForm\.title\)', '', text, flags=re.DOTALL)
text = re.sub(r'async def cmd_new_habit_removed\(.*?HabitCreationForm\.title\)', '', text, flags=re.DOTALL)
text = re.sub(r'from src\.db\.models import .*?Habit.*?\n', 'from src.db.models import Project, TimeLog\n', text)
text = text.replace('from src.bot.states import ProjectCreationForm, HabitCreationForm', 'from src.bot.states import ProjectCreationForm')
with open('src/bot/handlers/entities/commands.py', 'w') as f:
    f.write(text)

# entities/menu.py
with open('src/bot/handlers/entities/menu.py', 'r') as f:
    text = f.read()
text = re.sub(r'@router\.message\(F\.text == "🎯 Habits"\).*?sys_views\.msg_list_active_habits\(message, habits\)', '', text, flags=re.DOTALL)
text = re.sub(r'from src\.db\.models import Project, Habit', 'from src.db.models import Project', text)
with open('src/bot/handlers/entities/menu.py', 'w') as f:
    f.write(text)


# entities/router.py
with open('src/bot/handlers/entities/router.py', 'r') as f:
    text = f.read()
text = text.replace('from . import commands, menu, projects, habits', 'from . import commands, menu, projects')
text = text.replace('router.include_router(habits.router)', '')
with open('src/bot/handlers/entities/router.py', 'w') as f:
    f.write(text)

# intents/intent_entities.py
with open('src/bot/handlers/intents/intent_entities.py', 'r') as f:
    text = f.read()
text = text.replace("Project, Habit", "Project")
text = re.sub(r'elif entity_type == "habit":.*?elif entity_type == "project":', 'if entity_type == "project":', text, flags=re.DOTALL)
# For the rest of occurrences of habit in intent_entities.py
text = re.sub(r'elif entity_type == "habit":\s+hab = db\.query\(Habit\).*?Habit not found.*?\)', '', text, flags=re.DOTALL)
with open('src/bot/handlers/intents/intent_entities.py', 'w') as f:
    f.write(text)

# intents/intent_session.py
with open('src/bot/handlers/intents/intent_session.py', 'r') as f:
    text = f.read()
text = text.replace(', Habit', '')
with open('src/bot/handlers/intents/intent_session.py', 'w') as f:
    f.write(text)

print("done regex replacements for generic handlers")
