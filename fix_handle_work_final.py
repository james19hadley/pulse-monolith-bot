import re

with open('src/bot/handlers/ai_router.py', 'r') as f:
    text = f.read()

broken_code = """    from src.bot.handlers.utils import log_action
    new_state = {"project_id": project.id, "total_minutes_spent": project.total_minutes_spent}
    log_action(db, user.id, "LOG_WORK", old_state, new_state)"""

text = text.replace(broken_code, "")

with open('src/bot/handlers/ai_router.py', 'w') as f:
    f.write(text)
