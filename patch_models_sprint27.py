import re

with open("src/db/models.py", "r") as f:
    content = f.read()

# 1. Add fields to Project
project_patch = """    unit: Mapped[Optional[str]] = mapped_column(String, default="minutes")
    
    # --- Great Migration: Daily Quotas & Streaks ---
    daily_target_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # E.g., 15 (minutes or times)
    daily_progress: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_completions: Mapped[int] = mapped_column(Integer, default=0)
    # -----------------------------------------------
    
    next_action_text: Mapped[Optional[str]] = mapped_column(String, nullable=True) # E.g., "Read pointers chapter\""""

content = content.replace("    unit: Mapped[Optional[str]] = mapped_column(String, default=\"minutes\")\n    next_action_text: Mapped[Optional[str]] = mapped_column(String, nullable=True) # E.g., \"Read pointers chapter\"", project_patch)

# Also ensure `date` is imported from datetime if not already
if "from datetime import datetime, timezone" in content or "from datetime import datetime" in content:
    if "from datetime import datetime, date" not in content and "from datetime import date" not in content and "date," not in content and " date " not in content:
        content = content.replace("from datetime import datetime", "from datetime import datetime, date")

# Let's remove the Habit class completely.
# Find the start of class Habit(Base): and the next class TimeLog(Base)
habit_regex = re.compile(r'class Habit\(Base\):.*?class TimeLog\(Base\):', re.DOTALL)
if habit_regex.search(content):
    content = habit_regex.sub('class TimeLog(Base):', content)
else:
    print("Could not find Habit class block. Skipping removal, might be already removed.")

with open("src/db/models.py", "w") as f:
    f.write(content)

print("models.py patched")
