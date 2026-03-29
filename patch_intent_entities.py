import re

with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    content = f.read()

replacement = """
            if edit.action == "delete":
                prev_state = {"title": proj.title, "target_value": proj.target_value, "unit": proj.unit, "status": proj.status}
                proj.status = "archived" # Soft delete
                db.flush()
                alog = ActionLog(
                    user_id=user.id,
                    tool_name="delete_project",
                    previous_state_json=prev_state,
                    new_state_json={"id": proj.id, "status": "archived"}
                )
                db.add(alog)
                responses.append(f"🗑 Project deleted: <b>{proj.title}</b>")
                continue
            
            prev_state = {"title": proj.title, "target_value": proj.target"""

content = content.replace('            prev_state = {"title": proj.title, "target_value": proj.target', replacement)

replacement_habit = """
            if edit.action == "delete":
                prev_state = {"title": habit.title, "target_value": habit.target_value, "unit": habit.unit, "status": habit.status}
                habit.status = "archived" # Soft delete
                db.flush()
                alog = ActionLog(
                    user_id=user.id,
                    tool_name="delete_habit",
                    previous_state_json=prev_state,
                    new_state_json={"id": habit.id, "status": "archived"}
                )
                db.add(alog)
                responses.append(f"🗑 Habit deleted: <b>{habit.title}</b>")
                continue
            
            prev_state = {"title": habit.title, "target_value": habit.target"""

content = content.replace('            prev_state = {"title": habit.title, "target_value": habit.target', replacement_habit)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(content)
print("Intent entities patched.")
