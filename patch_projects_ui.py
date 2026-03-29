import re

with open("src/bot/handlers/entities/projects.py", "r") as f:
    text = f.read()

# Locate the formatting section for the project text.
# The text gets assembled from line 97
target_injection = """
            if getattr(proj, 'daily_target_value', None) is not None:
                streak = getattr(proj, 'current_streak', 0)
                daily_prog = getattr(proj, 'daily_progress', 0)
                emoji = "🔥" if streak > 0 else "🎯"
                text += f"\n{emoji} Daily Target: {daily_prog:g} / {proj.daily_target_value:g} {proj.unit or 'min'}"
                if streak > 0:
                    text += f" (Streak: {streak} days)"
"""

text = re.sub(r'text \+= f"\\n⏳ Time Tracked: \{total_hours:g\}h"', 
              'text += f"\\n⏳ Time Tracked: {total_hours:g}h"\n' + target_injection, 
              text)

text = re.sub(r'Status: \{proj.status\}"\n', 
              'Status: {proj.status}"\n' + target_injection, 
              text)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(text)

print("patched projects ui")
