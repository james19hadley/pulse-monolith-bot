with open("src/bot/handlers.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "await event.bot.send_message(" in line:
        new_lines.append(line)
        new_lines.append("                    event.from_user.id,\n")
        new_lines.append("                    f\"✅ I noticed you added me to the channel **{event.chat.title}**!\\nI\\'ve automatically set it as your target.\",\n")
        new_lines.append("                    parse_mode=\"Markdown\"\n")
        new_lines.append("                )\n")
        skip = True
    elif skip and "except Exception:" in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open("src/bot/handlers.py", "w") as f:
    f.writelines(new_lines)
print("done")
