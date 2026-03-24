with open('src/bot/handlers/settings_keys.py', 'r') as f:
    text = f.read()

import re

# Add imports
text = text.replace('from src.bot.keyboards import (', 'from src.bot.keyboards import (\n    get_catalyst_keyboard,\n    get_interval_keyboard,\n    get_channel_keyboard,')

# Add FSM states
state_class_match = re.search(r'class SettingsState\(StatesGroup\):.*?\n(.*?)\n\n', text, re.DOTALL)
if state_class_match and 'waiting_for_catalyst' not in state_class_match.group(1):
    text = text.replace('class SettingsState(StatesGroup):', 'class SettingsState(StatesGroup):\n    waiting_for_catalyst = State()\n    waiting_for_interval = State()\n    waiting_for_channel = State()')

# Add handlers
new_handlers = '''
# --- Catalyst ---
@router.callback_query(F.data == "settings_catalyst")
async def cq_settings_catalyst(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏱️ <b>Catalyst Limit</b> (Minutes)\\n\\nHow long before an overdue habit pushes a notification?",
        reply_markup=get_catalyst_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_catalyst_"))
async def cq_set_catalyst_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_catalyst_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me a number (in minutes) for the Catalyst Limit:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_catalyst)
        return
    
    try:
        limit = int(val)
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.catalyst_limit = limit
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_text(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(SettingsState.waiting_for_catalyst)
async def process_catalyst_text(message: Message, state: FSMContext):
    try:
        limit = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.catalyst_limit = limit
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_text(message.from_user.id)
        await message.answer(f"✅ Catalyst updated.\\n\\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid number.")

# --- Interval ---
@router.callback_query(F.data == "settings_interval")
async def cq_settings_interval(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏱️ <b>Ping Interval</b> (Minutes)\\n\\nHow often should I ping you if you are overdue?",
        reply_markup=get_interval_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_interval_"))
async def cq_set_interval_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_interval_", "")
    if val == "custom":
        await callback.message.edit_text(
            "Send me a number (in minutes) for the Ping Interval:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_interval)
        return
    
    try:
        limit = int(val)
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.interval_limit = limit
            db.commit()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    text, markup = get_control_panel_text(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(SettingsState.waiting_for_interval)
async def process_interval_text(message: Message, state: FSMContext):
    try:
        limit = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.interval_limit = limit
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_text(message.from_user.id)
        await message.answer(f"✅ Interval updated.\\n\\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid number.")

# --- Channel ---
@router.callback_query(F.data == "settings_channel")
async def cq_settings_channel(callback: CallbackQuery):
    await callback.message.edit_text(
        "📣 <b>Target Channel</b>\\n\\nWhere should I post reports?",
        reply_markup=get_channel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_channel_"))
async def cq_set_channel_action(callback: CallbackQuery, state: FSMContext):
    val = callback.data.replace("set_channel_", "")
    if val == "clear":
        with SessionLocal() as db:
            user = get_or_create_user(db, callback.from_user.id)
            user.target_channel_id = None
            db.commit()
        text, markup = get_control_panel_text(callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        return
        
    if val == "custom":
        await callback.message.edit_text(
            "Forward a message from your channel or send the ID:",
            reply_markup=get_back_settings_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_channel)
        return

@router.message(SettingsState.waiting_for_channel)
async def process_channel_text(message: Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())
        with SessionLocal() as db:
            user = get_or_create_user(db, message.from_user.id)
            user.target_channel_id = channel_id
            db.commit()
        await state.clear()
        
        text, markup = get_control_panel_text(message.from_user.id)
        await message.answer(f"✅ Channel updated.\\n\\n{text}", reply_markup=markup, parse_mode="HTML")
    except ValueError:
        await message.answer("Please send a valid ID.")

'''

if 'def cq_settings_catalyst' not in text:
    text += new_handlers

with open('src/bot/handlers/settings_keys.py', 'w') as f:
    f.write(text)
