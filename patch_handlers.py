import re

with open("src/bot/handlers/core.py", "r") as f:
    text = f.read()

# Remove habit references in undo command
text = re.sub(r'\s*elif tool == "create_habit":.*?parse_mode="HTML"\)', '', text, flags=re.DOTALL)
text = re.sub(r'\s*elif tool == "delete_habit":.*?parse_mode="HTML"\)', '', text, flags=re.DOTALL)
text = re.sub(r'\s*elif tool == "log_habit":.*?parse_mode="HTML"\)', '', text, flags=re.DOTALL)
text = re.sub(r'\s*elif data\.startswith\("undo_create_habit_"\):.*?already deleted."\)', '', text, flags=re.DOTALL)
text = re.sub(r'\s*elif data\.startswith\("undo_habit_"\):.*?already deleted."\)', '', text, flags=re.DOTALL)

# Re-match any remaining Habit models line
text = text.replace('ActionLog, Habit, Project, TimeLog', 'ActionLog, Project, TimeLog')
text = text.replace('ActionLog, Habit, Session, TimeLog', 'ActionLog, Session, TimeLog')

text = text.replace('/habit &lt;id/name&gt; [val] - Mark habit (e.g. /habit workout 1)\n', '')
text = text.replace('/undo - Revert the last time log or habit log', '/undo - Revert the last time log')
text = text.replace('/habits - List active habits and IDs\n', '')
text = text.replace('/new_habit &lt;name&gt; - Create a new habit\n', '')

with open("src/bot/handlers/core.py", "w") as f:
    f.write(text)

print("core.py patched.")
