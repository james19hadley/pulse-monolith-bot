import re

def repl(file, rules):
    try:
        with open(file, 'r') as f:
            c = f.read()
        for pat, rep in rules:
            if callable(rep):
                c = re.sub(pat, rep, c)
            else:
                c = c.replace(pat, rep)
        with open(file, 'w') as f:
            f.write(c)
    except Exception as e:
        print(f"Error {file}: {e}")

repl('src/ai/providers.py', [
    ('or habit', ''),
    ('and habit', ''),
    ('or a new habit', ''),
])

repl('src/core/prompts.py', [
    ('- LOG_HABIT: The user is reporting the completion of a daily habit or routine (e.g. "Did 10 pushups", "Read my pages").\n', ''),
    ('or a new habit. (e.g. "Create a project \'Write Book\' with a 50h goal", "создай проект Х и привычку Y")', '(e.g. "Create a project \'Write Book\' with a 50h goal", "создай проект Х")'),
    ('"Make my report strict without emojis", "Show habits first then focus time"', '"Make my report strict without emojis", "Show projects first then focus time"'),
    ('or habit (e.g. "Rename \'Coding\' to \'Backend Dev\'", "Change the habit target to 20 reps")', '(e.g. "Rename \'Coding\' to \'Backend Dev\'", "Change the project daily target to 20 reps")')
])

repl('src/ai/router.py', [
    ('LogHabitParams, ', ''),
])

with open("src/ai/router.py", "r") as f:
    text = f.read()
text = re.sub(r'def extract_log_habit.*?active_habits_text\)\n', '', text, flags=re.DOTALL)
with open("src/ai/router.py", "w") as f:
    f.write(text)

repl('src/bot/handlers/ai_router.py', [
    ('from src.bot.handlers.intents.intent_log_habit import _handle_log_habit\n', ''),
    ('# _handle_log_work, _handle_log_habit, _handle_session_control', '# _handle_log_work, _handle_session_control'),
    ('    IntentType.LOG_HABIT: _handle_log_habit,\n', '')
])

repl('src/core/personas.py', [
    ("track the user's habits, time logged on projects", "track the user's projects, time logged"),
    ("or completing 1 workout habit", "or completing a daily project goal")
])

repl('src/core/constants.py', [
    ('    LOG_HABIT = "LOG_HABIT"\n', '')
])

print("done")
