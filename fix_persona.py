with open("src/core/personas.py", "r") as f:
    text = f.read()

replacement = "CRITICAL FORMATTING RULES:\\nYour output must be strictly compatible with Telegram's HTML parse_mode. You MUST use <b>bold</b>, <i>italic</i>, <code>code</code> instead of Markdown. NEVER output **bold** or *italic* as it will fail or render raw stars.\\nIMPORTANT: NEVER wrap telegram slash commands (like /help, /projects) in backticks or HTML code tags. Just write them as plain text (e.g. use /help instead of <code>/help</code>) so that Telegram automatically parses them as clickable links."

text = text.replace("CRITICAL FORMATTING RULES:\\nYour output must be strictly compatible with Telegram's HTML parse_mode. You MUST use <b>bold</b>, <i>italic</i>, <code>code</code> instead of Markdown. NEVER output **bold** or *italic* as it will fail or render raw stars.", replacement)

with open("src/core/personas.py", "w") as f:
    f.write(text)

