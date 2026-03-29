import re

with open("src/bot/handlers/entities/projects.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False

for i in range(len(lines)):
    line = lines[i]
    if "if is_time_based:" in line and "hours =" in lines[i+1]:
        new_lines.append(line)
        new_lines.append("                hours = proj.target_value / 60 if proj.target_value > 0 else 0\n")
        new_lines.append('                text = f"📁 <b>{proj.title}</b>\\n\\nTarget Hours: {hours:g}h\\nTotal Tracked: {total_hours:g}h\\nToday Tracked: {today_hours:g}h\\n🕒 Last active: {last_active_str}\\n{progress_bar}\\nStatus: {proj.status}"\n')
        new_lines.append("            else:\n")
        new_lines.append('                text = f"📁 <b>{proj.title}</b>\\n\\nTarget: {proj.target_value:g} {proj.unit}\\nTotal Progress: {total_progress:g} {proj.unit}\\nToday Progress: {today_progress:g} {proj.unit}\\n🕒 Last active: {last_active_str}\\n{progress_bar}\\nStatus: {proj.status}"\n')
        new_lines.append("\n")
        new_lines.append("            if getattr(proj, 'daily_target_value', None) is not None:\n")
        new_lines.append("                streak = getattr(proj, 'current_streak', 0)\n")
        new_lines.append("                daily_prog = getattr(proj, 'daily_progress', 0)\n")
        new_lines.append('                emoji = "🔥" if streak > 0 else "🎯"\n')
        new_lines.append('                text += f"\\n{emoji} Daily Target: {daily_prog:g} / {proj.daily_target_value:g} {proj.unit or \'min\'}"\n')
        new_lines.append("                if streak > 0:\n")
        new_lines.append('                    text += f" (Streak: {streak} days)"\n')
        skip = True
    elif skip:
        if "from src.db.models import Task" in line:
            skip = False
            new_lines.append("\n")
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.writelines(new_lines)
