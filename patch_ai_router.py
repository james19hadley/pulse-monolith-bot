import os
file_path = "src/bot/handlers/ai_router.py"
with open(file_path, "r") as f:
    content = f.read()

# Add _handle_undo to imports from intent_core
content = content.replace(
    'from src.bot.handlers.intents.intent_core import _handle_chat, _handle_config_update, _handle_config_report',
    'from src.bot.handlers.intents.intent_core import _handle_chat, _handle_config_update, _handle_config_report, _handle_undo'
)

# Add UNDO to INTENT_HANDLERS
content = content.replace(
    'IntentType.CONFIG_REPORT: _handle_config_report,',
    'IntentType.CONFIG_REPORT: _handle_config_report,\n    IntentType.UNDO: _handle_undo,'
)

# Fix the routing logic
content = content.replace(
    'if intent == IntentType.UNDO:\n                    pass # Handled via callbacks usually, but if typed it would go to a special function\n                else:\n                    await handler(message, db, user, provider_name, api_key)',
    'await handler(message, db, user, provider_name, api_key)'
)

with open(file_path, "w") as f:
    f.write(content)
print("done")
