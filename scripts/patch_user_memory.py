import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.db.repo import engine

def apply_migration():
    """
    Applies the DB migration for Sprint 44 & 45.
    We use autocommit so that if one column already exists, it doesn't abort the transaction for the rest.
    """
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN user_memory JSON;"))
            print("✅ Successfully added 'user_memory' column to 'users' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'user_memory' already exists.")
            else:
                print(f"❌ Error adding column user_memory: {e}")
                
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN target_period VARCHAR DEFAULT 'daily';"))
            print("✅ Successfully added 'target_period' column to 'projects' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'target_period' already exists.")
            else:
                print(f"❌ Error adding column target_period: {e}")
                
        # Sprint 45 additions
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN reminder_time TIMESTAMP WITH TIME ZONE;"))
            print("✅ Successfully added 'reminder_time' column to 'tasks' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'reminder_time' already exists.")
            else:
                print(f"❌ Error adding column reminder_time: {e}")
                
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN is_reminder_sent BOOLEAN DEFAULT FALSE;"))
            print("✅ Successfully added 'is_reminder_sent' column to 'tasks' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'is_reminder_sent' already exists.")
            else:
                print(f"❌ Error adding column is_reminder_sent: {e}")

if __name__ == "__main__":
    apply_migration()