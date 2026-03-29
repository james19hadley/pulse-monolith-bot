import sys

with open("src/bot/handlers/core.py", "r") as f:
    text = f.read()

# Wait, why did the undo tool not work?
# "я создал привычку typing и потом в меню зашёл и нажал кнопку удалить другую привычку которая была уже и называлась "1""
# "и потом хотел протестировать undo но он отменил не удаление привычки "1" а создаение "typing""
# That means "удаление привычки" didn't log an ActionLog.
# Let's check how 'arch' is implemented in habits.py.
