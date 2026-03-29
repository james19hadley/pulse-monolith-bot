import re

with open("src/bot/handlers/intents/intent_log_work.py", "r") as f:
    text = f.read()

text = text.replace('TokenUsage, Project, TimeLog, Habit, Session', 'TokenUsage, Project, TimeLog, Session')
text = text.replace('extract_log_work, extract_log_habit, extract_session_control', 'extract_log_work, extract_session_control')

# Inject daily progress update
daily_update = """
    # Update Daily target if applicable
    if project.daily_target_value is not None:
        amount_to_add = logged_progress if logged_progress is not None else extraction.duration_minutes
        if amount_to_add > 0:
            project.daily_progress = (project.daily_progress or 0) + amount_to_add
            # For immediate user feedback in msg
            msg_lines.append(f"🔥 Daily target progress: {project.daily_progress:g} / {project.daily_target_value:g} {project.unit or 'minutes'}")

    db.commit()
    db.refresh(log_entry)
"""

text = text.replace('    db.commit()\n    db.refresh(log_entry)', daily_update)

with open("src/bot/handlers/intents/intent_log_work.py", "w") as f:
    f.write(text)

