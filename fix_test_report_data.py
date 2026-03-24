import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

old_stats = """        stats = {
            "total_tracked": 120,
            "focus_tracked": 90,
            "habits_list": ["Workout: 1/1", "Reading: 0/1"],
            "logs_list": ["Did some coding", "Finished the book"]
        }"""

new_stats = """        stats = {
            "focus_minutes": 150,
            "void_minutes": 30,
            "projects": {"Deep Work": 120, "Admin": 30},
            "habits": [
                {"title": "Workout", "current": 1, "target": 1},
                {"title": "Reading", "current": 0, "target": 1}
            ],
            "inbox_count": 3
        }"""

text = text.replace(old_stats, new_stats)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

