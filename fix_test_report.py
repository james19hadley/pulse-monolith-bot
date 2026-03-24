import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

# Make sure settings_test_report is in the callback router, we need a separate handler for settings_test_report since it triggers a report

new_handler = """
@router.callback_query(F.data == "settings_test_report")
async def cq_test_report(callback: CallbackQuery):
    from src.db.repo import SessionLocal
    from src.bot.handlers.utils import get_or_create_user
    from src.bot.views import generate_evening_report
    
    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id)
        bot_msg = await callback.message.answer("<i>Generating test report...</i>", parse_mode="HTML")
        report_text = await generate_evening_report(db, user)
        await callback.message.answer(report_text, parse_mode="HTML")
        await callback.message.delete()
        await callback.answer()
"""

if "cq_test_report" not in text:
    text += "\n" + new_handler

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

