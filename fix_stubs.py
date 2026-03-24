with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

# Replace the single monolithic router with independent ones, or just let it fall through
import re
new_text = re.sub(r'elif callback\.data == "settings_back":\n\s+await state\.clear\(\)\n\s+with SessionLocal\(\) as db:\n\s+user = get_or_create_user\(db, callback\.from_user\.id\)\n\s+text = get_control_panel_text\(user\)\n\s+await callback\.message\.edit_text\(text, parse_mode="HTML", reply_markup=get_settings_keyboard\(\)\)\n\s+await callback\.answer\(\)\n\s+else:\n\s+await callback\.answer\("Not implemented", show_alert=True\)', 
'''elif callback.data in ["settings_back", "settings_main"]:
            await state.clear()
            with SessionLocal() as db:
                user = get_or_create_user(db, callback.from_user.id)
                text = get_control_panel_text(user)
                await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_settings_keyboard())
            await callback.answer()
        else:
            # Let it fall through to the other handlers at the bottom!
            return''', text)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(new_text)

