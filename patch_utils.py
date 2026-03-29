import re

with open("src/bot/handlers/utils.py", "r") as f:
    text = f.read()

text = text.replace('user_habits = db.query(Habit).filter(Habit.user_id == user.id).all()', 
                    'user_habits = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None).all()')

text = text.replace('habits_data = [{"title": h.title, "current": h.current_value, "target": h.target_value, "unit": h.unit or ""} for h in user_habits]',
                    'habits_data = [{"title": h.title, "current": h.daily_progress or 0, "target": h.daily_target_value, "unit": h.unit or ""} for h in user_habits]')

text = text.replace('"habits": habits_data,', '"projects_daily": habits_data,')
text = text.replace('["focus", "habits", "inbox", "void"]', '["focus", "projects", "inbox", "void"]')

# We will let "projects_daily" be mapped in views.py if we see 'habits_data'. Wait, in views.py I renamed it to `stats.get('projects')`. Oh no, I renamed the `blocks` in views.py. Let me double check what I did in views.py
with open("src/bot/handlers/utils.py", "w") as f:
    f.write(text)

