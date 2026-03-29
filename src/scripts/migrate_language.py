from src.db.session import engine
from sqlalchemy import text

def run_migration():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'ru';"))
            print("Language column added successfully.")
        except Exception as e:
            print(f"Error (maybe already exists): {e}")

if __name__ == "__main__":
    run_migration()
