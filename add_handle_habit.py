import re

with open("src/bot/handlers/ai_router.py", "r") as f:
    text = f.read()

# Add import for extract_log_habit
text = text.replace("extract_system_config, extract_entities, generate_chat", "extract_system_config, extract_entities, generate_chat, extract_log_habit")

# Route LOG_HABIT
text = text.replace(
    'elif intent == IntentType.LOG_HABIT:\n            await message.answer("Intent detected: LOG_HABIT, but native implementation is missing currently.")',
    'elif intent == IntentType.LOG_HABIT:\n            return await _handle_log_habit(message, db, user, provider_name, real_api_key)'
)
# Note: actually it falls to `else: Intent detected: LOG_HABIT...`
