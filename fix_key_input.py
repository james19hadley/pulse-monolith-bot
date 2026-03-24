import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    orig = f.read()

old_end = """    await message.answer(f"✅ Setup Complete: <b>{provider_name.capitalize()}</b> key is securely saved and set as active.{test_msg}", parse_mode="HTML")
    await state.clear()"""

new_end = """    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        text = get_control_panel_text(user)
        await message.answer(
            f"✅ <b>Setup Complete:</b> {provider_name.capitalize()} key saved.{test_msg}\\n\\n" + text, 
            parse_mode="HTML", 
            reply_markup=get_settings_keyboard()
        )
    await state.clear()"""

orig = orig.replace(old_end, new_end.replace('\\\\', '\\'))

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(orig)
