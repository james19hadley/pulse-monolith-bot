import os
from sqlalchemy import create_engine, text

def main():
    database_url = os.getenv("DATABASE_URL", "postgresql://pulse:pulse@db:5432/pulse")
    engine = create_engine(database_url)
    with engine.connect() as conn:
        try:
            # Check if habits table exists
            res = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'habits');"))
            has_habits = res.scalar()
            
            if not has_habits:
                print("No habits table found or already migrated.")
                return
            
            # Fetch all habits
            habits_res = conn.execute(text("SELECT id, user_id, title, status, target_value, current_value, unit, type, total_completions, current_streak, last_reset_date FROM habits"))
            habits = habits_res.fetchall()
            
            migrated = 0
            for h in habits:
                h_id, u_id, title, status, t_val, c_val, unit, h_type, t_comp, c_strk, l_reset = h
                
                global_current_value = 0
                if unit in ["minutes", "hours", "times", "pages"]:
                    global_current_value = t_comp * t_val
                
                # Insert into projects
                conn.execute(text("""
                    INSERT INTO projects (user_id, title, status, target_value, current_value, unit, daily_target_value, daily_progress, current_streak, last_completed_date, total_completions)
                    VALUES (:u_id, :title, :status, 0, :g_val, :unit, :t_val, :c_val, :c_strk, :l_reset, :t_comp)
                """), {
                    "u_id": u_id,
                    "title": title,
                    "status": status,
                    "g_val": global_current_value,
                    "unit": unit,
                    "t_val": t_val,
                    "c_val": c_val,
                    "c_strk": c_strk,
                    "l_reset": l_reset,
                    "t_comp": t_comp
                })
                migrated += 1
            
            # Drop the habits table
            conn.execute(text("DROP TABLE habits"))
            conn.commit()
            print(f"Migration completed beautifully. Migrated {migrated} habits into projects.")
            
        except Exception as e:
            print("Error during PostgreSQL migration:", e)

if __name__ == "__main__":
    main()
