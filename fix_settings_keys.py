import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

# Fix imports
text = text.replace('from src.bot.keyboards import (', 'from src.bot.keyboards import (\n    get_catalyst_keyboard,\n    get_interval_keyboard,\n    get_channel_keyboard,\n    get_pulse_menu_keyboard,\n    get_cutoff_keyboard,')

# Add missing FSM state for cutoff
state_class_match = re.search(r'class SettingsState\(StatesGroup\):.*?\n(.*?)\n\n', text, re.DOTALL)
if 'waiting_for_cutoff' not in text:
    text = text.replace('waiting_for_channel = State()', 'waiting_for_channel = State()\n    waiting_for_cutoff = State()')

# Add handlers for Pulse and Cutoff
pulse_cutoff_handlers = '''
# --- Pulse Intervals Menu ---
@router.callback_query(F.data == "settings_pulse")
async def cq_settings_pulse(callback: CallbackQuery):
    await callback.message.edit_text(
        "💓 <b>Pulse Intervals</b>\\n\\nConfigure the catalyst threshold and ping frequency for your overdue habits.",
        reply_markup=get_pulse_menu_keyboard(),
        parse_mode="HTML"
    )

# --- Cutoff Time ---
@router.callback_query(F.data == "settings_cutoff")
async def cq_settings_cutoff(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏰ <b>Report Time (Day Cutoff)</b>\\n\\nWhen does your day end? I will send your Daily Accountability Report and wipe habits at this time.",
        reply_markup=get_cutoff_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_cutoff_"))
async def cq_set_cutoff_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_cutoff_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me the time for your day cutoff in HH:MM format (e.g., 23:30):",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_cutoff)
        return
    
    try:
        from datetime import time
        h, m = map(int, val.split(':'))
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.day_cutoff_time = time(h, m)
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_text(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@router.message(SettingsState.waiting_for_cutoff)
async def process_cutoff_text(message: Message, state: FSMContext):
    try:
        from datetime import time
        val = message.text.strip().replace('.', ':')
        h, m = map(int, val.split(':'))
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.day_cutoff_time = time(h, m)
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_text(message.from_user.id)
        await message.answer(f"✅ Cutoff time updated.\\n\\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid time like '23:00'.")

'''

if 'def cq_settings_pulse' not in text:
    text += pulse_cutoff_handlers

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

