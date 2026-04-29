from sqlalchemy import create_engine, text

def apply_migration():
    """
    Applies the DB migration for Sprint 44: User Memory
    """
    DB_URL = "sqlite:///db.sqlite3"
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        try:
            # SQLite does not have a native JSON type in older versions, but TEXT works the same
            # SQLAlchemy maps JSON to TEXT natively under the hood in SQLite.
            conn.execute(text("ALTER TABLE users ADD COLUMN user_memory JSON;"))
            print("✅ Successfully added 'user_memory' column to 'users' table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️ Column 'user_memory' already exists.")
            else:
                print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    apply_migration()