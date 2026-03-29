with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    text = f.read()

import re
# We need to replace the malformed block:
# projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
# ")
# for h in habits:
#     entities_list.append(f": {h.title} (ID: {h.id}, Target: {h.target_value} {h.unit or 'times'})")

proper_block = """    projects = db.query(Project).filter(Project.user_id == user.id, Project.status == 'active').all()
    entities_list = []
    for p in projects:
        entities_list.append(f"Project: {p.title} (ID: {p.id})")"""

text = re.sub(r'    projects = db\.query\(Project\).*?or \'times\'\}\)"\)', proper_block, text, flags=re.DOTALL)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(text)
