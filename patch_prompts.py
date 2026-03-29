import re

with open("src/core/prompts.py", "r") as f:
    content = f.read()

replacement = """5. EDIT_ENTITIES: If the user wants to rename, delete, or change parameters of existing projects or habits.
   - Example: 'переименуй проект Рутина в Операционку', 'удали привычку курить', 'измени цель для бега на 10'"""

content = re.sub(r'5\. EDIT_ENTITIES: If the user wants to rename or change parameters of existing projects or habits\.\n   - Example: .+', replacement, content)

with open("src/core/prompts.py", "w") as f:
    f.write(content)

