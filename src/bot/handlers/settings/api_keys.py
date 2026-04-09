"""
Handlers for the user to securely submit and store their own provider API Keys (BYOK).

@Architecture-Map: [HND-SET-APIKEYS]
@Docs: docs/07_ARCHITECTURE_MAP.md
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.db.models import User
from src.bot.states import AddKeyState
from src.core.security import encrypt_key, decrypt_key
from src.bot.keyboards import get_providers_keyboard, get_api_keys_manage_keyboard

router = Router()

@router.message(Command("add_key"))
async def cmd_add_key_flow(message: Message, state: FSMContext):
    await message.answer(
        "Select your AI Provider to securely configure your API key:",
        reply_markup=get_providers_keyboard()
    )
    await state.set_state(AddKeyState.waiting_for_provider)


@router.callback_query(AddKeyState.waiting_for_provider, F.data.startswith("provider_"))
async def process_provider_selection(callback: CallbackQuery, state: FSMContext):
    provider_name = callback.data.replace("provider_", "")
    await state.update_data(provider_name=provider_name)
    
    await callback.message.edit_text(
        f"You selected <b>{provider_name.capitalize()}</b>.\n\nPlease paste your API Key below.\n<i>(It will be safely encrypted in the database)</i>", 
        parse_mode="HTML"
    )
    await state.set_state(AddKeyState.waiting_for_key)
    await callback.answer()


@router.callback_query(F.data == "cancel_fsm")
async def process_fsm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        text = get_control_panel_text(user)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
    await callback.answer()


@router.message(AddKeyState.waiting_for_key)
async def process_key_input(message: Message, state: FSMContext):
    data = await state.get_data()
    provider_name = data.get("provider_name")
    raw_key = message.text.strip()
    alias = provider_name  # default alias
    
    encrypted = encrypt_key(raw_key)

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        keys_dict = dict(user.api_keys) if user.api_keys else {}
        keys_dict[alias] = {
            "provider": provider_name,
            "key": encrypted
        }
        user.api_keys = keys_dict
        user.llm_provider = alias
        db.commit()

    # Fast test ping for Google
    test_msg = ""
    if provider_name == "google":
        try:
            temp_prov = GoogleProvider(api_key=raw_key)
            resp, tok = temp_prov.generate_content("Say exactly: OK")
            test_msg = f"\n\n📡 Automatic Test Ping successful! Tokens used: {tok}"
        except Exception as e:
            test_msg = f"\n\n⚠️ Automatic Test Ping failed: {str(e)}"
    
    await message.answer(f"✅ Setup Complete: <b>{provider_name.capitalize()}</b> key is securely saved and set as active.{test_msg}", parse_mode="HTML")
    
    try:
        await message.delete()
        await message.answer("<i>(Your API key message was actively deleted from the screen for security)</i>", parse_mode="HTML")
    except Exception:
        pass
        
    await state.clear()


@router.message(Command("my_key"))
async def cmd_my_key(message: Message):
    """Checks the status of the user's current aliases."""
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        if keys:
            providers = ", ".join(f"<code>{k}</code>" for k in keys.keys())
            await message.answer(f"<b>Saved Keys (Aliases):</b> {providers}\n<b>Active AI Alias:</b> <code>{user.llm_provider}</code>\n\n<i>To switch your active key, you can use</i> <code>/use_key &lt;alias-name&gt;</code>", parse_mode="HTML")
        else:
            await message.answer("Status: No API key configured. Features limited. Use <code>/add_key google &lt;your_key&gt;</code>.", parse_mode="HTML")


@router.message(Command("use_key"))
async def cmd_use_key(message: Message, command: CommandObject):
    """Switches the active API key alias."""
    if not command.args:
        await message.answer("Usage: <code>/use_key &lt;alias&gt;</code>", parse_mode="HTML")
        return
        
    alias = command.args.strip().lower()
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        keys = user.api_keys
        
        if not keys or alias not in keys:
            await message.answer(f"Error: You do not have a key saved under the alias <code>{alias}</code>. Use <code>/my_key</code> to view your aliases.", parse_mode="HTML")
            return
            
        user.llm_provider = alias
        db.commit()
        
    await message.answer(f"✅ Active AI provider switched to <code>{alias}</code>", parse_mode="HTML")


@router.callback_query(F.data.startswith("switch_key_"))
async def cq_switch_key(callback: CallbackQuery):
    alias = callback.data.replace("switch_key_", "")
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        keys = user.api_keys
        
        if not keys or alias not in keys:
            await callback.answer(f"Error: Key {alias} not found.", show_alert=True)
            return
            
        user.llm_provider = alias
        db.commit()
        
        # Re-render the keys menu
        msg = "<b>API Keys</b>\n\nYou have configured:\n"
        for k in keys.keys():
            msg += f" ✅ <code>{k}</code>\n"
            
        await callback.message.edit_text(
            msg,
            reply_markup=get_api_keys_manage_keyboard(keys, user.llm_provider),
            parse_mode="HTML"
        )
        await callback.answer(f"Switched to {alias}!")


