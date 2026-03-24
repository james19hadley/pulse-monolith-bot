with open("src/bot/handlers/ai_router.py", "r") as f:
    text = f.read()

text = text.replace(
    'f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\n"',
    'f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\\n" \\'
)

text = text.replace(
    'f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)"\n        f"🏃 Total: ',
    'f"✅ <b>{habit.title}</b> logged! (+{extraction.amount_completed} completion)\\n" \\\n        f"🏃 Total: '
)

with open("src/bot/handlers/ai_router.py", "w") as f:
    f.write(text)
