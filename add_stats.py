with open('src/bot/handlers.py', 'r') as f:
    text = f.read()

stats_cmd = """
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

@router.message(Command("settings"))
"""

text = text.replace('@router.message(Command("settings"))', stats_cmd)

with open('src/bot/handlers.py', 'w') as f:
    f.write(text)
