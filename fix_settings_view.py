with open('src/bot/handlers/settings_keys.py', 'r') as f:
    text = f.read()

old_block = """        provider = user.llm_provider or "None"
        persona = user.persona_type or "monolith"
        tz = user.timezone or "UTC"
        report_time = getattr(user, 'report_time', '20:00 (default)')

        text = (
            "⚙️ <b>Control Panel</b>\\n\\n"
            f"<b>Active AI:</b> <code>{provider}</code>\\n"
            f"<b>Persona:</b> <code>{persona}</code>\\n"
            f"<b>Timezone:</b> <code>{tz}</code>\\n"
            f"<b>Reports:</b> <code>{report_time}</code>\\n\\n"
            "<i>Select an option below to manage settings:</i>"
        )"""

new_block = """        provider = user.llm_provider or "None"
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
"""

if old_block in text:
    text = text.replace(old_block, new_block)
    with open('src/bot/handlers/settings_keys.py', 'w') as f:
        f.write(text)
    print("Replaced!")
else:
    print("Block not found!")
