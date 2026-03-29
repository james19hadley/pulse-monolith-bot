with open("src/bot/handlers/core.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "@router.callback_query(F.data.startswith(\"undo_\"))" in line:
        skip = True
    if skip and line.strip() == "await callback.answer()":
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open("src/bot/handlers/core.py", "w") as f:
    f.writelines(new_lines)
print("Removed old inline undo handler.")
