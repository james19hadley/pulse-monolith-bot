import re

with open('src/bot/handlers/ai_router.py', 'r') as f:
    text = f.read()

old_err = """        elif intent == IntentType.ERROR:
            import html
            safe_err = html.escape(str(error_msg)) if error_msg else "Unknown API error"
            await message.answer(f"I encountered an error connecting to the AI provider.\\n\\nError details:\\n<code>{safe_err}</code>", parse_mode="HTML")"""

new_err = """        elif intent == IntentType.ERROR:
            import html
            raw_err = str(error_msg) if error_msg else ""
            safe_err = html.escape(raw_err) if raw_err else "Unknown API error"
            
            if "429" in raw_err or "quota" in raw_err.lower():
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔑 Add / Change API Key", callback_data="settings_keys")
                ]])
                msg = (
                    "⚠️ <b>AI Provider Quota Exceeded</b>\\n\\n"
                    "It looks like you've hit the limit for the current API key. "
                    "Please add a new key or switch AI providers to continue."
                )
                await message.answer(msg, parse_mode="HTML", reply_markup=keyboard)
            else:
                await message.answer(f"I encountered an error connecting to the AI provider.\\n\\nError details:\\n<code>{safe_err}</code>", parse_mode="HTML")"""

if "elif intent == IntentType.ERROR:" in text:
    text = text.replace(old_err, new_err)
    with open('src/bot/handlers/ai_router.py', 'w') as f:
        f.write(text)
