import re

with open('src/bot/handlers.py', 'r') as f:
    original_code = f.read()

# I want to extract EVERYTHING before F.text.
parts = original_code.split('@router.message(F.text)')
before_f_text = parts[0]

# And the handler handle_freeform_text itself
# I can find where handle_freeform_text ends by removing everything from 'def log_tokens' and '@router.message(Command("stats"))'
after_f_text = '@router.message(F.text)' + parts[1]

# Let's cleanly split out log_tokens and cmd_stats. We know they are at the end.
# We strip them by finding the first occurrence of `def log_tokens` or `@router.message(Command("stats"))` in the after_f_text part.
if 'def log_tokens' in after_f_text:
    after_f_text = after_f_text.split('def log_tokens')[0]
if '@router.message(Command("stats"))' in after_f_text:
    after_f_text = after_f_text.split('@router.message(Command("stats"))')[0]
# Also if we mistakenly appended log_tokens before F.text, let's clean before_f_text
if 'def log_tokens' in before_f_text:
    before_f_text = before_f_text.split('def log_tokens')[0]
if '@router.message(Command("stats"))' in before_f_text:
    before_f_text = before_f_text.split('@router.message(Command("stats"))')[0]

log_and_stats_code = """
def log_tokens(telegram_id: int, usage_data: dict):
    if not usage_data: return
    try:
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                tu = TokenUsage(
                    user_id=user.id,
                    prompt_tokens=usage_data.get('prompt_tokens', 0),
                    completion_tokens=usage_data.get('completion_tokens', 0),
                    total_tokens=usage_data.get('total_tokens', 0),
                    model_name=usage_data.get('model_name', 'unknown')
                )
                db.add(tu)
                db.commit()
    except Exception as e:
        print(f"Error logging tokens: {e}")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    \"\"\"Shows AI Token Usage\"\"\"
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        prompt_total = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        comp_total = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        
        cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30
        
        await message.answer(
            f"📊 *FinOps / Token Usage*\\n"
            f"Input Tokens: `{prompt_total}`\\n"
            f"Output Tokens: `{comp_total}`\\n"
            f"Estimated Cost: `${cost:.5f}`\\n",
            parse_mode="Markdown"
        )
"""

new_code = before_f_text.rstrip() + "\n\n" + log_and_stats_code.strip() + "\n\n" + after_f_text.strip() + "\n"

with open('src/bot/handlers.py', 'w') as f:
    f.write(new_code)
