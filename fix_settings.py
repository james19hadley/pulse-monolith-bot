import re

with open('src/bot/handlers.py', 'r') as f:
    content = f.read()

# Replace the command logic for settings wrapper to include both. 

old_cmd = """
@router.message(Command("settings"))
async def cmd_settings(message: Message, command: CommandObject):
    if not command.args:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            threshold = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes else 60
            await message.answer(
                f"⚙️ **Current Settings**\\n"
                f"Catalyst Ping Threshold: `{threshold} minutes`\\n\\n"
                f"To change the heartbeat threshold, use:\\n`/settings catalyst <minutes>`",
                parse_mode="Markdown"
            )
        return

    parts = command.args.split(maxsplit=1)
    if parts[0].lower() == "catalyst":
        if len(parts) < 2 or not parts[1].isdigit():
            await message.answer("Error: Provide minutes. Example: `/settings catalyst 30`", parse_mode="Markdown")
            return
            
        minutes = int(parts[1])
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.catalyst_threshold_minutes = minutes
            db.commit()
            await message.answer(f"✅ Catalyst heartbeat threshold updated to `{minutes} minutes`.", parse_mode="Markdown")
        return
        
    await message.answer("Unknown setting. Try `/settings` to see options.", parse_mode="Markdown")
"""

new_cmd = """
@router.message(Command("settings"))
async def cmd_settings(message: Message, command: CommandObject):
    if not command.args:
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            threshold = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes else 60
            interval = user.catalyst_interval_minutes if user.catalyst_interval_minutes else 20
            await message.answer(
                f"⚙️ **Current Settings**\\n"
                f"Catalyst Ping Threshold: `{threshold} minutes`\\n"
                f"Catalyst Repeat Interval: `{interval} minutes` (0 to disable)\\n\\n"
                f"To change threshold, use: `/settings catalyst <minutes>`\\n"
                f"To change interval, use: `/settings interval <minutes>`",
                parse_mode="Markdown"
            )
        return

    parts = command.args.split(maxsplit=1)
    action = parts[0].lower()
    if action in ["catalyst", "interval"]:
        if len(parts) < 2 or not parts[1].isdigit():
            await message.answer(f"Error: Provide minutes. Example: `/settings {action} 30`", parse_mode="Markdown")
            return
            
        minutes = int(parts[1])
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            if action == "catalyst":
                user.catalyst_threshold_minutes = minutes
                msg = f"✅ Catalyst heartbeat threshold updated to `{minutes} minutes`."
            else:
                user.catalyst_interval_minutes = minutes
                msg = f"✅ Catalyst repeat interval updated to `{minutes} minutes`."
                if minutes == 0:
                    msg += " Pings disabled."
            db.commit()
            await message.answer(msg, parse_mode="Markdown")
        return
        
    await message.answer("Unknown setting. Try `/settings` to see options.", parse_mode="Markdown")
"""

content = content.replace(old_cmd.strip(), new_cmd.strip())

with open('src/bot/handlers.py', 'w') as f:
    f.write(content)

