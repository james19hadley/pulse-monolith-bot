with open("src/bot/handlers/entities/projects.py", "r") as f:
    lines = f.readlines()

out = []
i = 0
while i < len(lines):
    line = lines[i]
    if "today_progress = sum([l.progress_amount or 0 for l in logs if l.created_at >= today_start and l.progress_amount])" in line:
        out.append(line)
        out.append("            total_progress = sum([l.progress_amount or 0 for l in logs if l.progress_amount])\n")
        out.append("\n")
        out.append("            total_hours = total_minutes / 60\n")
        out.append("            today_hours = today_minutes / 60\n")
        out.append("            \n")
        out.append("            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']\n")
        out.append("\n")
        out.append("            progress_bar = \"\"\n")
        out.append("            if proj.target_value > 0:\n")
        out.append("                if is_time_based:\n")
        out.append("                    pct = min(1.0, (total_minutes / proj.target_value) if proj.target_value else 0)\n")
        out.append("                else:\n")
        out.append("                    pct = min(1.0, (total_progress / proj.target_value) if proj.target_value else 0)\n")
        out.append("                filled = int(pct * 10)\n")
        out.append("                progress_bar = \"\\nProgress: [\" + \"█\" * filled + \"░\" * (10 - filled) + f\"] {pct*100:.1f}%\\n\"\n")
        out.append("                \n")
        out.append("            if is_time_based:\n")
        out.append("                hours = proj.target_value / 60 if proj.target_value > 0 else 0\n")
        out.append("                text = f\"📁 <b>{proj.title}</b>\\n\\nTarget Hours: {hours:g}h\\nTotal Tracked: {total_hours:g}h\\nToday Tracked: {today_hours:g}h\\n🕒 Last active: {last_active_str}\\n{progress_bar}\\nStatus: {proj.status}\"\n")
        out.append("            else:\n")
        out.append("                text = f\"📁 <b>{proj.title}</b>\\n\\nTarget: {proj.target_value:g} {proj.unit}\\nTotal Progress: {total_progress:g} {proj.unit}\\nToday Progress: {today_progress:g} {proj.unit}\\n🕒 Last active: {last_active_str}\\n{progress_bar}\\nStatus: {proj.status}\"\n")
        out.append("                text += f\"\\n⏳ Time Tracked: {total_hours:g}h\"\n")
        out.append("\n")
        
        while "text += f\"\\n📈 Daily Progress: {today_progress:g} {proj.unit}\"" not in lines[i]:
            i += 1
        i += 1 # skip this line
        continue
    out.append(line)
    i+=1

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.writelines(out)

