import re

with open("src/ai/providers.py", "r") as f:
    text = f.read()

text = text.replace(
    'amount_completed: int = Field(description="The numeric amount completed. If user just says \'did pushups\', default to 1 unless specified.", default=1)',
    'amount_completed: int = Field(description="The numeric amount completed. If user just says \'did pushups\', default to 1 unless specified.", default=1)\n    unmatched_habit_name: Optional[str] = Field(description="If no habit matches, provide the inferred name of the new habit here (e.g. \'Drink water\').", default=None)'
)

with open("src/ai/providers.py", "w") as f:
    f.write(text)

