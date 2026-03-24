import re
with open("src/bot/handlers/settings_keys.py", "r") as f:
    orig = f.read()

old_cancel = """@router.callback_query(F.data == "cancel_fsm")
async def process_fsm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Operation cancelled.")
    await callback.answer()"""

new_cancel = """@router.callback_query(F.data == "cancel_fsm")
async def process_fsm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer()"""

orig = orig.replace(old_cancel, new_cancel)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(orig)
