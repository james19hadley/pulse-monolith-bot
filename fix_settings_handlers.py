import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    orig = f.read()

# Make sure imports are correct
orig = orig.replace(
    "from src.bot.keyboards import get_providers_keyboard, get_settings_keyboard",
    "from src.bot.keyboards import get_providers_keyboard, get_settings_keyboard, get_persona_keyboard, get_reports_keyboard, get_timezone_keyboard, get_back_settings_keyboard"
)

# Replace the text block explicitly correctly avoiding parsing backslash hell

builder_fn = '''
def get_control_panel_text(user) -> str:
    provider = user.llm_provider or "None"
    persona = user.persona_type or "monolith"
    tz = user.timezone or "UTC"
    cutoff = getattr(user, 'day_cutoff_time', '23:00')
    channel = getattr(user, 'target_channel_id', 'None')
    catalyst = getattr(user, 'catalyst_threshold_minutes', 60)
    interval = getattr(user, 'catalyst_interval_minutes', 20)

    config = user.report_config
    if isinstance(config, str):
        import json
        try:
            config = json.loads(config)
        except:
            config = None
    if not config:
        config = {"destination": "dm"}
        
    reports = config.get('destination', 'dm')

    return (
        f"⚙️ <b>Pulse Monolith Control Panel</b>\\n\\n"
        f"<code>catalyst</code>: {catalyst} <i>(Catalyst Ping Threshold)</i>\\n"
        f"<code>interval</code>: {interval} <i>(Catalyst Repeat Interval)</i>\\n"
        f"<code>channel</code>: {channel} <i>(Target Channel ID)</i>\\n"
        f"<code>report</code>: {reports} <i>(Dest: dm / channel / none)</i>\\n"
        f"<code>cutoff</code>: {cutoff} <i>(Day Cutoff Time)</i>\\n"
        f"<code>timezone</code>: {tz} <i>(Timezone)</i>\\n"
        f"<code>persona</code>: {persona} <i>(Bot Persona)</i>\\n"
        f"<code>provider</code>: {provider} <i>(Active LLM Provider)</i>\\n\\n"
        f"To change settings, you can simply text me (e.g. <code>\\'set timezone to Europe/London\\'</code>).\\n\\n"
        f"<i>Select an option below for quick actions:</i>"
    )

@router.message(F.text == "⚙️ Settings")
'''

orig = orig.replace('@router.message(F.text == "⚙️ Settings")', builder_fn.replace('\\\\', '\\'))

old_generate = '''        provider = user.llm_provider or "None"
        persona = user.persona_type or "monolith"
        tz = user.timezone or "UTC"
        cutoff = getattr(user, 'day_cutoff_time', '23:00')
        channel = getattr(user, 'target_channel_id', 'None')
        catalyst = getattr(user, 'catalyst_threshold_minutes', 60)
        interval = getattr(user, 'catalyst_interval_minutes', 20)

        # Checking report block config
        config = user.report_config
        if isinstance(config, str):
            import json
            try:
                config = json.loads(config)
            except:
                config = None
        if not config:
            config = {"destination": "dm"}
            
        reports = config.get('destination', 'dm')

        text = "⚙️ <b>Pulse Monolith Control Panel</b>\\n\\n"
        text += f"<code>catalyst</code>: {catalyst} <i>(Catalyst Ping Threshold)</i>\\n"
        text += f"<code>interval</code>: {interval} <i>(Catalyst Repeat Interval)</i>\\n"
        text += f"<code>channel</code>: {channel} <i>(Target Channel ID)</i>\\n"
        text += f"<code>report</code>: {reports} <i>(Dest: dm / channel / none)</i>\\n"
        text += f"<code>cutoff</code>: {cutoff} <i>(Day Cutoff Time)</i>\\n"
        text += f"<code>timezone</code>: {tz} <i>(Timezone)</i>\\n"
        text += f"<code>persona</code>: {persona} <i>(Bot Persona)</i>\\n"
        text += f"<code>provider</code>: {provider} <i>(Active LLM Provider)</i>\\n\\n"
        text += "To change settings, you can simply text me (e.g. <code>'set timezone to Europe/London'</code> or <code>'disable reports'</code>).\\n\\n"
        text += "<i>Select an option below for quick actions:</i>"
        await message.answer(text, parse_mode="HTML", reply_markup=get_settings_keyboard())'''

new_generate = '''        text = get_control_panel_text(user)
        await message.answer(text, parse_mode="HTML", reply_markup=get_settings_keyboard())'''

orig = orig.replace(old_generate.replace('\\\\', '\\'), new_generate)

callbacks_old = """        elif callback.data == "settings_persona":
            msg = "To change persona, just tell me! E.g. 'Act like a sarcastic butler'"
            await callback.answer(msg, show_alert=True)
        elif callback.data == "settings_timezone":
            msg = "To change timezone, just tell me! E.g. 'Set my timezone to Europe/London'"
            await callback.answer(msg, show_alert=True)
        elif callback.data == "settings_reports":
            msg = "To change report config, ask me naturally! E.g. 'Move my daily report to 11 PM'"
            await callback.answer(msg, show_alert=True)"""

callbacks_new = '''        elif callback.data == "settings_persona":
            await callback.message.edit_text("<b>Choose a Persona:</b>\\n\\nEach persona has a different style.", parse_mode="HTML", reply_markup=get_persona_keyboard())
            await callback.answer()
        elif callback.data == "settings_timezone":
            await callback.message.edit_text("<b>Select your Timezone:</b>", parse_mode="HTML", reply_markup=get_timezone_keyboard())
            await callback.answer()
        elif callback.data == "settings_reports":
            await callback.message.edit_text("<b>Report Destination:</b>\\n\\nWhere should I send your daily Evening Report?", parse_mode="HTML", reply_markup=get_reports_keyboard())
            await callback.answer()
        elif callback.data == "settings_back":
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                text = get_control_panel_text(user)
                await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
            await callback.answer()'''

orig = orig.replace(callbacks_old, callbacks_new.replace('\\\\', '\\'))

subhandlers = """
@router.callback_query(F.data.startswith("set_persona_"))
async def cq_set_persona(callback: CallbackQuery):
    persona = callback.data.replace("set_persona_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        user.persona_type = persona
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Persona set to {persona.capitalize()}!")

@router.callback_query(F.data.startswith("set_tz_"))
async def cq_set_tz(callback: CallbackQuery):
    tz = callback.data.replace("set_tz_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        user.timezone = tz
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Timezone set to {tz}!")

@router.callback_query(F.data.startswith("set_report_"))
async def cq_set_report(callback: CallbackQuery):
    dest = callback.data.replace("set_report_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        config = user.report_config
        import json
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}
        if not config: config = {}
        config['destination'] = dest
        user.report_config = config
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer(f"Report destination set to {dest}!")
"""
orig += subhandlers

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(orig)
print("done")
