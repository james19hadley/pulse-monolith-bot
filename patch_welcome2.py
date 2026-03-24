import re

with open("src/bot/views.py", "r") as f:
    text = f.read()

# Replace the examples and add the help note
old_examples = """    msg += "<b>Examples of what you can say:</b>\\n"
    msg += "• <i>\\"Create a new project for learning Python\\"</i>\\n"
    msg += "• <i>\\"I just worked out for 45 minutes\\"</i>\\n"
    msg += "• <i>\\"Set my timezone like in Houston and post my daily report exactly at midnight\\"</i>\\n\\n" """

new_examples = """    msg += "<b>Examples of what you can say:</b>\\n"
    msg += "• <i>\\"Расскажи о том что ты умеешь\\"</i>\\n"
    msg += "• <i>\\"Create a new project for learning Python\\"</i>\\n"
    msg += "• <i>\\"I just worked out for 45 minutes\\"</i>\\n"
    msg += "• <i>\\"Set my timezone like in Houston and post my daily report exactly at midnight\\"</i>\\n\\n" """

text = text.replace(old_examples, new_examples)

old_connected = 'msg += "✅ <i>AI Engine Connected. Start typing to begin!</i>\\n"'
new_connected = 'msg += "✅ <i>AI Engine Connected. Start typing to begin!</i>\\n\\n📖 <b>Tip:</b> You can read the guide by clicking the <b>❓ Help</b> button below or using the /help command."\n'

text = text.replace(old_connected, new_connected)

with open("src/bot/views.py", "w") as f:
    f.write(text)

