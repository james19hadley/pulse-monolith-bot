import sqlite3
import os

DB_PATH = 'pulse.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Add fields to projects table
    columns_to_add = [
        ("daily_target_value", "INTEGER DEFAULT NULL"),
        ("daily_progress", "INTEGER DEFAULT 0"),
        ("current_streak", "INTEGER DEFAULT 0"),
        ("last_completed_date", "DATE DEFAULT NULL"),
        ("total_completions", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in columns_to_add:
        # Avoid crashing if columns already exist
        try:
            c.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to projects.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                pass
            else:
                print(f"Error adding {col_name}:", e)

    # 2. Port habits to projects
    try:
        # Check if habits table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='habits'")
        if not c.fetchone():
            print("No habits table found or already migrated.")
            return

        c.execute("SELECT id, user_id, title, status, target_value, current_value, unit, type, total_completions, current_streak, last_reset_date FROM habits")
        habits = c.fetchall()
        
        migrated_count = 0
        for h in habits:
            h_id, u_id, title, status, t_val, c_val, unit, h_type, t_comp, c_strk, l_reset = h
            
            # Map values
            # Using global target_value = 0 (infinite or non-defined global limit)
            # daily_target_value = t_val
            # daily_progress = c_val
            # total_completions = t_comp
            # current_streak = c_strk
            
            # Note: projects table already has target_value, current_value, unit
            # We map target_value to daily_target_value
            # We map current_value to daily_progress
            # For the global current_value, we might just set it to 0 or total_completions * target_value (if numeric)
            global_current_value = 0
            if unit in ["minutes", "hours", "times", "pages"]:
               global_current_value = t_comp * t_val
               
            c.execute("""
                INSERT INTO projects (user_id, title, status, target_value, current_value, unit, daily_target_value, daily_progress, current_streak, last_completed_date, total_completions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (u_id, title, status, 0, global_current_value, unit, t_val, c_val, c_strk, l_reset, t_comp))
            migrated_count += 1
            
        print(f"Migrated {migrated_count} habits to projects.")
        
        # Now drop the habits table
        c.execute("DROP TABLE habits")
        print("Dropped old habits table.")
        
        conn.commit()
    except Exception as e:
        print("Error during migration:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

