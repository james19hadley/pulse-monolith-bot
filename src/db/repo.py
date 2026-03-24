import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

# Load environment variables
load_dotenv()

# Get DB URL, fallback to local sqlite if not found
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

# Fix for older docker/heroku setups that might use 'postgres://' instead of 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite strictly needs check_same_thread=False, but Postgres rejects it
# Turn off echo in production so we don't spam the logs with SQL queries
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL connection
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# Create a customized Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Creates all tables in the database based on the models defined in metadata.
    """
    print(f"Initializing database at {DATABASE_URL}...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")

if __name__ == "__main__":
    init_db()

def get_admin_metrics():
    from src.db.models import User, Session, TimeLog, TokenUsage
    from sqlalchemy import func
    import datetime
    with SessionLocal() as db:
        users_count = db.query(User).count()
        total_tokens = db.query(func.sum(TokenUsage.total_tokens)).scalar() or 0
        active_sessions = db.query(Session).filter(Session.end_time == None).count()
        today = datetime.datetime.now().date()
        total_time_today = db.query(func.sum(TimeLog.duration_minutes)).filter(
            func.date(TimeLog.created_at) == today
        ).scalar() or 0
        return {
            "Total Users": users_count,
            "Total Tokens Used": total_tokens,
            "Active Focus Sessions": active_sessions,
            "Total Focused Minutes Today": total_time_today
        }
