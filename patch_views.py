import re

with open("src/bot/views.py", "r") as f:
    text = f.read()

text = text.replace('build habits, and destroy procrastination.', 'build projects, and destroy procrastination.')
text = re.sub(r'# Habit\n.*?def habit_updated_message.*?target\}"\n', '', text, flags=re.DOTALL)

text = text.replace('["focus", "habits", "inbox", "void"]', '["focus", "projects_daily", "inbox", "void"]')
text = text.replace('"habits": "📈"', '"projects_daily": "📈"')

# Rename block
text = text.replace('elif block == "habits":', 'elif block == "projects_daily":')
text = text.replace("habits = stats.get('habits', [])", "habits = stats.get('projects_daily', [])")
text = text.replace("e['habits']", "e['projects_daily']")
text = text.replace("<b>Habits:</b>", "<b>Daily Targets:</b>")

with open("src/bot/views.py", "w") as f:
    f.write(text)

print("patched views")
