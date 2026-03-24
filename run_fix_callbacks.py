with open('src/bot/handlers/settings_keys.py', 'r') as f:
    text = f.read()

# Instead of regex, split on parts
parts1 = text.split('@router.callback_query(F.data == "settings_keys")')
head = parts1[0]
tail = parts1[1]

parts2 = tail.split('@router.message(Command("add_key"))')
tail2 = '@router.message(Command("add_key"))' + parts2[1]

new_block = """@router.callback_query(F.data.startswith("settings_"))
async def cq_settings_stubs(callback: CallbackQuery, state: FSMContext):
    if callback.data == "settings_keys":
        await callback.message.edit_text(
            "Select your AI Provider to securely configure your API key:",
            reply_markup=get_providers_keyboard()
        )
        await state.set_state(AddKeyState.waiting_for_provider)
        await callback.answer()
    elif callback.data == "settings_persona":
        msg = "To change persona, just tell me! E.g. 'Act like a sarcastic butler' or use /settings persona sarcastic"
        await callback.answer(msg, show_alert=True)
    elif callback.data == "settings_timezone":
        msg = "To change timezone, just tell me! E.g. 'Set my timezone to Europe/London'"
        await callback.answer(msg, show_alert=True)
    elif callback.data == "settings_reports":
        msg = "To change report config, ask me naturally! E.g. 'Move my daily report to 11 PM'"
        await callback.answer(msg, show_alert=True)
    else:
        await callback.answer()

"""

with open('src/bot/handlers/settings_keys.py', 'w') as f:
    f.write(head + new_block + tail2)

