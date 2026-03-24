import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    orig = f.read()

# I want to replace the body of cq_settings_stubs with a try-except
new_body = """
@router.callback_query(F.data.startswith("settings_"))
async def cq_settings_stubs(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "settings_keys":
            await callback.message.edit_text(
                "Select your AI Provider to securely configure your API key:",
                reply_markup=get_providers_keyboard()
            )
            await state.set_state(AddKeyState.waiting_for_provider)
            await callback.answer()
        elif callback.data == "settings_persona":
            msg = "To change persona, just tell me! E.g. 'Act like a sarcastic butler'"
            await callback.answer(msg, show_alert=True)
        elif callback.data == "settings_timezone":
            msg = "To change timezone, just tell me! E.g. 'Set my timezone to Europe/London'"
            await callback.answer(msg, show_alert=True)
        elif callback.data == "settings_reports":
            msg = "To change report config, ask me naturally! E.g. 'Move my daily report to 11 PM'"
            await callback.answer(msg, show_alert=True)
        else:
            await callback.answer("Not implemented", show_alert=True)
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Callback error: {traceback.format_exc()}")
        await callback.answer(f"Error: {e}", show_alert=True)
"""

# use regex to replace it
pattern = re.compile(r'@router\.callback_query\(F\.data\.startswith\("settings_"\)\).*?else:\s+await callback\.answer\(\)', re.DOTALL)
if pattern.search(orig):
    fixed = pattern.sub(new_body.strip(), orig)
    with open("src/bot/handlers/settings_keys.py", "w") as f:
        f.write(fixed)
    print("Replaced!")
else:
    print("Not found")
