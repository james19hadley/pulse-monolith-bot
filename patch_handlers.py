with open('src/bot/handlers.py', 'a') as f:
    f.write('''

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
        
        # Approximate cost for Gemini 2.5 Flash
        # $0.075 per 1M input, $0.30 per 1M output
        cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30
        
        await message.answer(
            f"📊 *FinOps / Token Usage*\\n"
            f"Input Tokens: `{prompt_total}`\\n"
            f"Output Tokens: `{comp_total}`\\n"
            f"Estimated Cost: `${cost:.5f}`\\n",
            parse_mode="Markdown"
        )
''')
