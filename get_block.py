with open("src/bot/handlers/entities/projects.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines[80:108]):
    print(f"{i+80}: {line.rstrip()}")
