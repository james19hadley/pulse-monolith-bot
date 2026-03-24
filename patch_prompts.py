import re

with open('src/core/personas.py', 'r') as f:
    content = f.read()

# Replace the specific help text in the core_context
old_text = "If they ask what you can do, explain these core features. NEVER hallucinate features you don't have.\n\nYou also have specific manual slash commands if the user prefers them or gets confused: /help, /projects, /habits, /new_project, /new_habit, /settings, /persona, /tokens. Remind them to use /help to see all of them."
new_text = "Wait for the user to ask what you can do before dumping feature lists. Do NOT dump manual slash commands or long capability descriptions unless the user explicitly asks for help, asks what you can do, or says they are lost. Just respond directly and concisely to their current request."

if old_text in content:
    content = content.replace(old_text, new_text)

with open('src/core/personas.py', 'w') as f:
    f.write(content)
