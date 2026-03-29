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

            # Ensure projects table has the new columns
            print("Adding daily fields to the projects table if they do not exist...")
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS daily_target_value INTEGER;"))
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS daily_progress INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS last_completed_date DATE;"))
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS total_completions INTEGER DEFAULT 0;"))
            conn.commit()
            
            # Get columns that actually exist in the habits table
            cols_res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'habits'"))
            existing_columns = [row[0] for row in cols_res.fetchall()]

            # Fetch all habits
            habits_res = conn.execute(text(f"SELECT * FROM habits"))
            habits = habits_res.mappings().all()
            
            migrated = 0
            for h in habits:
                u_id = h.get("user_id")
                title = h.get("title", "Untitled Habit")
                status = h.get("status", "active")
                t_val = h.get("target_value", 1)
                c_val = h.get("current_value", 0)
                unit = h.get("unit", "times")
                h_type = h.get("type", "counter")
                t_comp = h.get("total_completions", 0)
                c_strk = h.get("current_streak", 0)
                l_reset = h.get("last_reset_date", None)
                
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
