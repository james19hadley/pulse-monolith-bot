import re

with open('src/bot/handlers.py', 'r') as f:
    content = f.read()

# Add import for registry if not there
if 'USER_SETTINGS_REGISTRY' not in content:
    content = content.replace('from src.core.config import TELEGRAM_BOT_TOKEN', 'from src.core.config import TELEGRAM_BOT_TOKEN, USER_SETTINGS_REGISTRY')

# Find the cmd_settings function block and replace it
def find_and_replace_settings():
    lines = content.split('\n')
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith('@router.message(Command("settings"))'):
            start_idx = i
            break
            
    if start_idx != -1:
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith('def log_tokens') or lines[i].startswith('@router.message'):
                end_idx = i
                break
                
    if start_idx != -1 and end_idx != -1:
        new_cmd = """@router.message(Command("settings"))
async def cmd_settings(message: Message, command: CommandObject):
    \"\"\"Update user preferences via config registry.\"\"\"
    if not command.args:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            
            msg = "⚙️ **Current Settings**\\n\\n"
            for key, meta in USER_SETTINGS_REGISTRY.items():
                val = getattr(user, meta['db_column'])
                if val is None:
                    val = meta['default']
                msg += f"*{meta['name']}*:\\n`{val}` ({meta['description']})\\nChange: `/settings {key} <value>`\\n\\n"
                
            await message.answer(msg, parse_mode="Markdown")
        return

    parts = command.args.split(maxsplit=1)
    key = parts[0].lower()
    
    if key not in USER_SETTINGS_REGISTRY:
        await message.answer(f"Unknown setting '{key}'. Try `/settings` to see options.", parse_mode="Markdown")
        return
        
    if len(parts) < 2:
        await message.answer(f"Error: Provide a value. Example: `/settings {key} 30`", parse_mode="Markdown")
        return
        
    val_str = parts[1]
    meta = USER_SETTINGS_REGISTRY[key]
    
    try:
        val = meta['type'](val_str)
    except ValueError:
        await message.answer(f"Error: Value must be of type {meta['type'].__name__}.", parse_mode="Markdown")
        return
        
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        setattr(user, meta['db_column'], val)
        db.commit()
        await message.answer(f"✅ Setting `{key}` updated to `{val}`.", parse_mode="Markdown")
"""
        
        return '\n'.join(lines[:start_idx]) + '\n' + new_cmd + '\n' + '\n'.join(lines[end_idx:])
    
    return content

new_content = find_and_replace_settings()

with open('src/bot/handlers.py', 'w') as f:
    f.write(new_content)
