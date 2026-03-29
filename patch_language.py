from sqlalchemy import text
from src.db.repo import SessionLocal

with SessionLocal() as db:
    db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR DEFAULT 'Russian';"))
    db.commit()
    print("Migrated successfully")
