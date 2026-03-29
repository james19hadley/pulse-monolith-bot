import sys
import re

with open("src/bot/handlers/entities/habits.py", "r") as f:
    text = f.read()

target = """        if action == "arch":
            db.delete(hab)
            db.commit()
            await cb.answer(f"Deleted {hab.title}.")
            await cb_habits_list(cb, state)"""

new_text = """        if action == "arch":
            # We must log this to Undo
            from src.db.models import ActionLog
            al = ActionLog(
                user_id=user.id,
                tool_name="delete_habit",
                previous_state_json={"habit_id": hab.id, "title": hab.title, "target_value": hab.target_value, "current_value": hab.current_value},
                new_state_json={}
            )
            db.add(al)
            db.delete(hab)
            db.commit()
            await cb.answer(f"Deleted {hab.title}.")
            await cb_habits_list(cb, state)"""

if target in text:
    text = text.replace(target, new_text)
    with open("src/bot/handlers/entities/habits.py", "w") as f:
        f.write(text)
    print("Fixed habit arch")
else:
    # Just insert it directly using regex
    pattern = r'if action == "arch":\s*db.delete\(hab\)\s*db.commit\(\)\s*await cb.answer\(f"Deleted \{hab.title\}\."\)\s*await cb_habits_list\(cb, state\)'
    
    text = re.sub(pattern, new_text.strip(), text)
    with open("src/bot/handlers/entities/habits.py", "w") as f:
        f.write(text)
    print("Fixed via regex")

