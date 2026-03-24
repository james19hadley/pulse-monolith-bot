import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    orig = f.read()

# Make sure imports are added
from_import = "get_back_settings_keyboard"
if "get_api_keys_manage_keyboard" not in orig:
    orig = orig.replace(from_import, from_import + ", get_api_keys_manage_keyboard")

if "from src.bot.states import AddKeyState" in orig:
    orig = orig.replace("from src.bot.states import AddKeyState", "from src.bot.states import AddKeyState, SettingsState")

# Replace settings_keys block
old_keys = """        if callback.data == "settings_keys":
            await callback.message.edit_text(
                "Select your AI Provider to securely configure your API key:",
                reply_markup=get_providers_keyboard()
            )
            await state.set_state(AddKeyState.waiting_for_provider)
            await callback.answer()"""

new_keys = """        if callback.data == "settings_keys":
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                keys = user.api_keys or {}
                if not keys:
                    msg = "<b>API Keys</b>\\n\\nYou have no keys configured yet."
                else:
                    msg = "<b>API Keys</b>\\n\\nYou have configured:\\n"
                    for k in keys.keys():
                        msg += f"✅ <code>{k}</code>\\n"
            await callback.message.edit_text(
                msg,
                reply_markup=get_api_keys_manage_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
        elif callback.data == "settings_add_key":
            await callback.message.edit_text(
                "Select your AI Provider to securely configure your API key:",
                reply_markup=get_providers_keyboard()
            )
            await state.set_state(AddKeyState.waiting_for_provider)
            await callback.answer()"""

orig = orig.replace(old_keys, new_keys.replace('\\\\', '\\'))

# Timezone block adjust
old_tz = """        elif callback.data == "settings_timezone":
            await callback.message.edit_text("<b>Select your Timezone:</b>", parse_mode="HTML", reply_markup=get_timezone_keyboard())
            await callback.answer()"""

new_tz = """        elif callback.data == "settings_timezone":
            await callback.message.edit_text("<b>Select your Timezone:</b>\\n\\nChoose from below, or just type your city/offset in the chat (e.g. 'Moscow', 'UTC+3', '+03:00') right now.", parse_mode="HTML", reply_markup=get_timezone_keyboard())
            await state.set_state(SettingsState.waiting_for_tz_text)
            await callback.answer()"""

orig = orig.replace(old_tz, new_tz.replace('\\\\', '\\'))

# Handle when going to settings_back -> clear states
old_back = """        elif callback.data == "settings_back":
            with SessionLocal() as db:"""
new_back = """        elif callback.data == "settings_back":
            await state.clear()
            with SessionLocal() as db:"""
orig = orig.replace(old_back, new_back)

# Process manual TZ input handler at the end of the file
manual_tz = """
@router.message(SettingsState.waiting_for_tz_text)
async def process_manual_tz(message: Message, state: FSMContext):
    tz = message.text.strip()
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        user.timezone = tz
        db.commit()
        db.refresh(user)
        text = get_control_panel_text(user)
        await message.answer(f"✅ Timezone set to {tz}\\n\\n" + text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await state.clear()
"""

orig += manual_tz

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(orig)

print("done")
