import os
file_path = "src/bot/handlers/intents/intent_core.py"
with open(file_path, "a") as f:
    f.write("""

async def _handle_undo(message: Message, db, user, provider_name, api_key):
    from src.bot.handlers.core import cmd_undo
    # Since cmd_undo uses SessionLocal anyway, we can just call it
    # We pass None for state since it handles it
    await cmd_undo(message, state=None)
""")
print("done")
