import sys

with open('src/bot/handlers.py', 'r') as f:
    content = f.read()

# Make sure imports are complete
imports = """
from src.bot.views import (
    welcome_message, 
    session_started_message, 
    session_already_active_message,
    no_active_session_message,
    session_ended_message,
    project_created_message,
    project_list_message,
    stats_message,
    settings_list_message,
    habit_created_message,
    habit_updated_message,
    inbox_saved_message,
    undo_success_message,
    undo_fail_message,
    nothing_to_undo_message
)
"""

if 'stats_message' not in content:
    # Replace the old view imports
    old_imports = """from src.bot.views import (
    welcome_message, 
    session_started_message, 
    session_already_active_message,
    no_active_session_message,
    session_ended_message,
    project_created_message,
    project_list_message
)"""
    content = content.replace(old_imports, imports.strip())

# Replace new_habit
content = content.replace('f"✅ Created Habit: `[{new_habit.id}]` {new_habit.title} (Target: {new_habit.target_value})"', 'habit_created_message(new_habit.id, new_habit.title, new_habit.target_value)')

# Replace log_habit
content = content.replace('f"📈 Habit `{habit.title}` updated: {habit.current_value}/{habit.target_value}"', 'habit_updated_message(habit.title, habit.current_value, habit.target_value)')

# Replace inbox 
content = content.replace('f"📥 Saved to Inbox: _{params.raw_content}_"', 'inbox_saved_message(params.raw_content)')

# Replace undo msgs
content = content.replace('"⚠️ Nothing to undo."', 'nothing_to_undo_message()')
content = content.replace('"⏪ Undo successful: Removed Time Log."', 'undo_success_message("Time Log")')
content = content.replace('"⏪ Undo successful: Reverted Habit progress."', 'undo_success_message("Habit progress")')
content = content.replace('"⚠️ Cannot undo that specific action type yet."', 'undo_fail_message()')

# Write back
with open('src/bot/handlers.py', 'w') as f:
    f.write(content)
