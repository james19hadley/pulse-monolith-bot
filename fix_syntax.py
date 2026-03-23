with open('src/bot/handlers.py', 'r') as f:
    text = f.read()

text = text.replace('f"📊 *FinOps / Token Usage*\n"', 'f"📊 *FinOps / Token Usage*\\n"')
text = text.replace('f"Input Tokens: `{prompt_total}`\n"', 'f"Input Tokens: `{prompt_total}`\\n"')
text = text.replace('f"Output Tokens: `{comp_total}`\n"', 'f"Output Tokens: `{comp_total}`\\n"')
text = text.replace('f"Estimated Cost: `${cost:.5f}`\n",', 'f"Estimated Cost: `${cost:.5f}`\\n",')

with open('src/bot/handlers.py', 'w') as f:
    f.write(text)
