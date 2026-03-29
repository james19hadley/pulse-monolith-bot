with open("src/bot/handlers/sessions.py", "r") as f:
    text = f.read()

replacement = """                session.status = "closed"
                
                from src.bot.handlers.utils import get_or_create_project_zero
                p_zero = get_or_create_project_zero(db, user.id)

                log = TimeLog(
                    user_id=user.id,
                    session_id=session.id,
                    duration_minutes=actual_duration_minutes,
                    project_id=p_zero.id,
                    description="Completed Focus Session (End of Day)"
                )
                db.add(log)
                p_zero.current_value = (p_zero.current_value or 0) + actual_duration_minutes
                if p_zero.daily_target_value is not None:
                    p_zero.daily_progress = (p_zero.daily_progress or 0) + actual_duration_minutes
            user.active_session_id = None"""

old_str = """                session.status = "closed"
                
                log = TimeLog(
                    user_id=user.id,
                    session_id=session.id,
                    duration_minutes=actual_duration_minutes,
                    project_id=None,
                    description="Completed Focus Session (End of Day)"
                )
                db.add(log)
            user.active_session_id = None"""

text = text.replace(old_str, replacement)
with open("src/bot/handlers/sessions.py", "w") as f:
    f.write(text)
print("done")
