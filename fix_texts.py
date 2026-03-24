import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    content = f.read()

def replace_func(func_name, new_body):
    pattern = r"async def " + func_name + r"\(.*?\)[\s\S]*?(?=\n(?:@|async def|# ---))"
    global content
    content = re.sub(pattern, "async def " + func_name + "(callback: CallbackQuery):\n" + new_body + "\n", content, count=1)

pulse_body = """    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        catalyst = getattr(user, 'catalyst_limit', 60)
        interval = getattr(user, 'interval_limit', 20)
    
    text = (
        "💓 <b>Pulse Intervals</b>\\n\\n"
        "• <b>Catalyst Limit</b>: How long (in minutes) to wait after a deadline before pushing the first notification.\\n"
        "• <b>Ping Interval</b>: How frequently (in minutes) to repeat the notification if the habit remains overdue.\\n\\n"
        f"<b>Current Settings:</b>\\n"
        f"Catalyst: <code>{catalyst}</code> min\\n"
        f"Ping: <code>{interval}</code> min"
    )
    await callback.message.edit_text(text, reply_markup=get_pulse_menu_keyboard(), parse_mode="HTML")"""
replace_func("cq_settings_pulse", pulse_body)

catalyst_body = """    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'catalyst_limit', 60)
    text = f"⏱️ <b>Catalyst Limit</b> (Minutes)\\n\\n<i>How much time should pass after the deadline before I notify you?</i>\\n\\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_catalyst_keyboard(), parse_mode="HTML")"""
replace_func("cq_settings_catalyst", catalyst_body)

interval_body = """    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'interval_limit', 20)
    text = f"⏱️ <b>Ping Interval</b> (Minutes)\\n\\n<i>How often should I ping you to remind you about the overdue habit?</i>\\n\\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_interval_keyboard(), parse_mode="HTML")"""
replace_func("cq_settings_interval", interval_body)

channel_body = """    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'target_channel_id', 'None')
    text = f"📣 <b>Target Channel</b>\\n\\nWhere should I post reports?\\n\\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_channel_keyboard(), parse_mode="HTML")"""
replace_func("cq_settings_channel", channel_body)

cutoff_body = """    with SessionLocal() as db:
        from src.bot.handlers.utils import get_or_create_user
        user = get_or_create_user(db, callback.from_user.id)
        current = getattr(user, 'day_cutoff_time', '23:00')
    text = f"⏰ <b>Day Cutoff Time</b>\\n\\nAt what time should the day end for reporting purposes? (Format: HH:MM)\\n\\n<b>Current:</b> <code>{current}</code>"
    await callback.message.edit_text(text, reply_markup=get_cutoff_keyboard(), parse_mode="HTML")"""
replace_func("cq_settings_cutoff", cutoff_body)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(content)
