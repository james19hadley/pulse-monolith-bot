import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    text = f.read()

new_func = """
@router.message(Command("tokens"))
async def cmd_tokens(message: Message):
    \"\"\"Shows AI Token Usage\"\"\"
    from datetime import datetime, timezone, timedelta
    
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id)
        
        # Total
        prompt_total = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        comp_total = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id).scalar() or 0
        cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30

        # Today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        prompt_today = db.query(func.sum(TokenUsage.prompt_tokens)).filter(TokenUsage.user_id == user.id, TokenUsage.created_at >= today_start).scalar() or 0
        comp_today = db.query(func.sum(TokenUsage.completion_tokens)).filter(TokenUsage.user_id == user.id, TokenUsage.created_at >= today_start).scalar() or 0
        cost_today = (prompt_today / 1000000.0) * 0.075 + (comp_today / 1000000.0) * 0.30
        
        msg = f"📊 <b>Token Usage Statistics</b>\\n\\n"
        msg += f"<b>Today (UTC):</b>\\n"
        msg += f"• Prompts: <code>{prompt_today}</code>\\n"
        msg += f"• Completions: <code>{comp_today}</code>\\n"
        msg += f"• Est. Cost: <b>${cost_today:.4f}</b>\\n\\n"
        
        msg += f"<b>All-Time:</b>\\n"
        msg += f"• Prompts: <code>{prompt_total}</code>\\n"
        msg += f"• Completions: <code>{comp_total}</code>\\n"
        msg += f"• Est. Cost: <b>${cost:.4f}</b>"

        await message.answer(msg, parse_mode="HTML")
"""

text = re.sub(r'@router\.message\(Command\("tokens"\)\)[\s\S]*?await message\.answer\(msg, parse_mode="HTML"\)', new_func.strip(), text)

with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(text)

