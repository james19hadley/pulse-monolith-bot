import re

with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    text = f.read()

# 1. Clean out the creation of habits via NLP
# The whole block for 'h in extraction.habits:' should just be gone since providers doesn't return extraction.habits
text = re.sub(r'if getattr\(extraction, "habits", None\):.*?# Flush.*?\n', '', text, flags=re.DOTALL)
text = text.replace("I could not determine the exact details for the project or habit to create.", "I could not determine the exact details for the project to create.")

# 2. Clean out editing capabilities for habits
text = re.sub(r'from src\.db\.models import Project(.*?)\n', r'from src.db.models import Project\n', text)
text = re.sub(r'habits = db.query\(Habit\).*?entities_list\.append\(.*?\)\s*', '', text, flags=re.DOTALL)
text = re.sub(r'elif entity_type == "habit":.*?msg \+= f" \(Target: \{habit\.target_value\} \{habit\.unit or \'times\'\}\)"\n.*?responses\.append\(msg\)\s*', '', text, flags=re.DOTALL)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(text)
