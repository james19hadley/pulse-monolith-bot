import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.db.repo import engine

def apply_migration():
    """
    Applies the DB migration for Sprint 44: User Memory
    """
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN user_memory JSON;"))
            print("✅ Successfully added 'user_memory' column to 'users' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️ Column 'user_memory' already exists.")
            else:
                print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    apply_migration()