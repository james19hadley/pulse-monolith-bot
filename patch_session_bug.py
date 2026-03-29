import re

with open("src/bot/handlers/intents/intent_session.py", "r") as f:
    text = f.read()

# Fix the incorrect variable unpacking and check
text = text.replace(
    'params, err = extract_session_control(message.text, provider_name, api_key)',
    'params, tokens = extract_session_control(message.text, provider_name, api_key)'
)

# And fix the if condition
text = text.replace(
    'if err or not params:',
    'if not params:'
)

# We should also log tokens!
replacement = """
    params, tokens = extract_session_control(message.text, provider_name, api_key)
    if tokens:
        from src.bot.handlers.utils import log_tokens
        log_tokens(db, user.id, tokens)
        
    if not params:
"""

text = re.sub(r'    params, tokens = extract_session_control\(message.text, provider_name, api_key\)\n    if not params:', replacement, text)


with open("src/bot/handlers/intents/intent_session.py", "w") as f:
    f.write(text)

