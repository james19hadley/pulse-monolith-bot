import sys

with open("src/bot/handlers/core.py", "r") as f:
    text = f.read()

# Replace async def cmd_undo(message: Message):
# with async def cmd_undo(message: Message, state: FSMContext):
text = text.replace("async def cmd_undo(message: Message):", "async def cmd_undo(message: Message, state: FSMContext):")

with open("src/bot/handlers/core.py", "w") as f:
    f.write(text)

