import re
with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    orig = f.read()

s1 = """        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg, parse_mode="HTML")"""

r1 = """        msg = f"✅ Project created: <b>{proj.title}</b>"
        if proj.target_value > 0:
            if getattr(proj, 'unit', None) and proj.unit not in ['minutes', 'hours']:
                msg += f" (Target: {proj.target_value} {proj.unit})"
            else:
                msg += f" (Target: {proj.target_value / 60:g}h)"
        await message.answer(msg, parse_mode="HTML")"""

orig = orig.replace(s1, r1)

with open("src/bot/handlers/intents/intent_entities.py", "w") as f:
    f.write(orig)

