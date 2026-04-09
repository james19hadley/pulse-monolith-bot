"""
Single-run migration script to populate a default language column for users in the database.

@Architecture-Map: [SCRIPT-MIGRATE-LANG]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import asyncio
from sqlalchemy.orm import Session
from src.db.repo import SessionLocal
from src.db.models import User

def migrate_languages():
    with SessionLocal() as db:
        users = db.query(User).all()
        count = 0
        for u in users:
            if not u.language:
                u.language = "ru"
                count += 1
        db.commit()
        print(f"Migrated {count} users to fallback language 'ru'.")

if __name__ == "__main__":
    migrate_languages()
