import re
with open("src/bot/handlers/entities/projects.py", "r") as f:
    orig = f.read()

s1 = """            today_progress = sum([l.progress_amount or 0 for l in logs if l.created_at >= today_start and l.progress_amount])

            hours = proj.target_value / 60 if proj.target_value > 0 else 0
            total_hours = total_minutes / 60
            today_hours = today_minutes / 60
            
            progress_bar = ""
            if proj.target_value > 0:
                pct = min(1.0, total_minutes / proj.target_value)
                filled = int(pct * 10)
                progress_bar = "\nProgress: [" + "█" * filled + "░" * (10 - filled) + f"] {pct*100:.1f}%\n"
                
            text = f"📁 <b>{proj.title}</b>\n\nTarget Hours: {hours:g}h\nTotal Tracked: {total_hours:g}h\nToday Tracked: {today_hours:g}h\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
            if proj.unit and proj.unit != 'minutes':
                text += f"\n📈 Daily Progress: {today_progress:g} {proj.unit}"
"""

r1 = """            today_progress = sum([l.progress_amount or 0 for l in logs if l.created_at >= today_start and l.progress_amount])
            total_progress = sum([l.progress_amount or 0 for l in logs if l.progress_amount])

            total_hours = total_minutes / 60
            today_hours = today_minutes / 60
            
            is_time_based = not proj.unit or proj.unit in ['minutes', 'hours']

            progress_bar = ""
            if proj.target_value > 0:
                if is_time_based:
                    pct = min(1.0, (total_minutes / proj.target_value) if proj.target_value else 0)
                else:
                    pct = min(1.0, (total_progress / proj.target_value) if proj.target_value else 0)
                filled = int(pct * 10)
                progress_bar = "\nProgress: [" + "█" * filled + "░" * (10 - filled) + f"] {pct*100:.1f}%\n"
                
            if is_time_based:
                hours = proj.target_value / 60 if proj.target_value > 0 else 0
                text = f"📁 <b>{proj.title}</b>\n\nTarget: {hours:g}h\nTotal Tracked: {total_hours:g}h\nToday Tracked: {today_hours:g}h\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
            else:
                text = f"📁 <b>{proj.title}</b>\n\nTarget: {proj.target_value} {proj.unit}\nTotal Progress: {total_progress:g} {proj.unit}\nToday Progress: {today_progress:g} {proj.unit}\n🕒 Last active: {last_active_str}\n{progress_bar}\nStatus: {proj.status}"
                text += f"\n⏳ Time Tracked: {total_hours:g}h"
"""

orig = orig.replace(s1, r1)

with open("src/bot/handlers/entities/projects.py", "w") as f:
    f.write(orig)

