import re
with open("src/ai/providers.py", "r") as f:
    orig = f.read()

orig = orig.replace(
    'target_value: int = Field(description="The target estimated effort value. If they specify hours, multiply by 60. Default is 0.", default=0)',
    'target_value: int = Field(description="The target estimated effort value. If they specify hours, multiply by 60. Default is 0.", default=0)\n    unit: Optional[str] = Field(description="The unit of measurement (e.g. pages, pages, reps, hours, minutes). Default is minutes.", default="minutes")'
)

with open("src/ai/providers.py", "w") as f:
    f.write(orig)

