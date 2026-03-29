import re

with open("src/scheduler/jobs.py", "r") as f:
    text = f.read()

# 1. Fix imports
text = text.replace(" Habit, ", " ")

# 2. Fix evening_nudge_job
evening_nudge_old = """                # Find lagging habits
                habits = db.query(Habit).filter(Habit.user_id == user.id, Habit.nudge_threshold_days > 0).all()
                lagging_habits = []
                for h in habits:
                    last_update = h.updated_at if h.updated_at else h.created_at
                    if last_update:
                        last_update = last_update.replace(tzinfo=None) # naive comparison
                        since_update = (now - last_update).days
                        if since_update >= h.nudge_threshold_days:
                            lagging_habits.append(h.title)"""
                            
evening_nudge_new = """                # Find lagging projects that act as routines
                projects = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None).all()
                lagging_habits = []
                for p in projects:
                    last_update = p.last_completed_date if p.last_completed_date else (p.updated_at.date() if p.updated_at else p.created_at.date())
                    if last_update:
                        since_update = (now.date() - last_update).days
                        if since_update >= 3: # default nudge threshold 3 days
                            lagging_habits.append(p.name)"""                            
text = text.replace(evening_nudge_old, evening_nudge_new)

midnight_job = """
@shared_task(name="job_midnight_reset")
def midnight_reset_job():
    \"\"\"
    Runs at midnight. Inspects all Projects with a daily_target_value.
    Calculates if daily_progress >= daily_target_value. If yes, bump total_completions.
    If no, break current_streak = 0.
    Finally, reset project.daily_progress = 0.
    \"\"\"
    now = datetime.utcnow()
    with SessionLocal() as db:
        users = db.query(User).all()
        for user in users:
            # Assumes cutoff checked hourly, but for simplicity let's assume this strictly runs when now.hour == user.day_cutoff_time.hour
            if now.hour == user.day_cutoff_time.hour and 0 <= now.minute < 60:
                projects = db.query(Project).filter(Project.user_id == user.id, Project.daily_target_value != None).all()
                for p in projects:
                    if p.daily_progress >= p.daily_target_value:
                        p.total_completions = (p.total_completions or 0) + 1
                        # We don't increment streak here because that might be done instantly on log, or we do it here. 
                        # Actually, keeping streak intact if they hit it.
                    else:
                        p.current_streak = 0
                    p.daily_progress = 0
                db.commit()
"""

# append to end
text += midnight_job

with open("src/scheduler/jobs.py", "w") as f:
    f.write(text)

