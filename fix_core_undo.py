import sys

with open("src/bot/handlers/core.py", "r") as f:
    text = f.read()

target = """            elif tool == "log_habit":
                hid = action.new_state_json.get("habit_id")"""
                
new_text = """            elif tool == "delete_habit":
                title = action.previous_state_json.get("title")
                target_value = action.previous_state_json.get("target_value")
                current_value = action.previous_state_json.get("current_value")
                h = Habit(user_id=action.user_id, title=title, target_value=target_value, current_value=current_value)
                db.add(h)
                await message.answer(f"↩️ Habit deletion undone: <b>{title}</b>", parse_mode="HTML")

            elif tool == "log_habit":
                hid = action.new_state_json.get("habit_id")"""

if "delete_habit" not in text:
    text = text.replace(target, new_text)
    with open("src/bot/handlers/core.py", "w") as f:
        f.write(text)
    print("Fixed core.py undo")

