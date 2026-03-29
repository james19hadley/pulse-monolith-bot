import re
with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    text = f.read()

# Fix the dangling `habit` variables from create logic
text = re.sub(r'        alog = ActionLog\(user_id=user\.id, tool_name="create_habit".*?\n', '', text, flags=re.DOTALL)
text = re.sub(r'        await message\.answer\(f"✅ created: <b>\{habit\.title\}</b>", parse_mode="HTML"\)\n', '', text, flags=re.DOTALL)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(text)
