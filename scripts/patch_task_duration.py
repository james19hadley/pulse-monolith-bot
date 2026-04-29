import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.db.repo import engine

def apply_migration():
    """
    Applies the DB migration for Sprint 46.
    """
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN estimated_minutes INTEGER;"))
            print("✅ Successfully added 'estimated_minutes' column to 'tasks' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'estimated_minutes' already exists.")
            else:
                print(f"❌ Error adding column estimated_minutes: {e}")

if __name__ == "__main__":
    apply_migration()