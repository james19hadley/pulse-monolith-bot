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
    
    @Architecture-Map: [DB-CORE-SESSION]
    @Docs: docs/reference/07_ARCHITECTURE_MAP.md
    """

    print(f"Initializing database at {DATABASE_URL}...")
    Base.metadata.create_all(bind=engine)
    
    # --- AUTO MIGRATION: ADD MISSING COLUMNS ---
    from sqlalchemy import text as sql_text
    try:
        with engine.begin() as conn:
            # Check for PostgreSQL or SQLite
            if "sqlite" in DATABASE_URL:
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_target_value INTEGER"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_progress INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN current_streak INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN last_completed_date DATE"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN total_completions INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE sessions ADD COLUMN rest_start_time TIMESTAMP"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_target_value INTEGER"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_progress INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN current_streak INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN last_completed_date DATE"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN total_completions INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE sessions ADD COLUMN save_state_context VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'ru'"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE tasks ADD COLUMN is_focus_today BOOLEAN DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN parent_id INTEGER REFERENCES projects(id) ON DELETE SET NULL"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE sessions ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE time_logs ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE users ADD COLUMN talkativeness_level VARCHAR DEFAULT 'standard'"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE users ADD COLUMN reflection_config JSON"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE users ADD COLUMN last_evening_plan VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE users ADD COLUMN show_ai_spinner BOOLEAN DEFAULT TRUE"))
                except Exception:
                    pass
            else:
                # PostgreSQL
                columns_to_add = [
                    ("users", "report_config", "JSON"),
                    ("users", "language", "VARCHAR DEFAULT 'ru'"),
                    ("users", "talkativeness_level", "VARCHAR DEFAULT 'standard'"),
                    ("users", "reflection_config", "JSON"),
                    ("users", "last_evening_plan", "VARCHAR"),
                    ("users", "show_ai_spinner", "BOOLEAN DEFAULT TRUE"),
                    ("projects", "daily_target_value", "INTEGER"),
                    ("projects", "daily_progress", "INTEGER DEFAULT 0"),
                    ("projects", "current_streak", "INTEGER DEFAULT 0"),
                    ("projects", "last_completed_date", "DATE"),
                    ("projects", "total_completions", "INTEGER DEFAULT 0"),
                    ("projects", "unit", "VARCHAR"),
                    ("projects", "next_action_text", "VARCHAR"),
                    ("time_logs", "progress_amount", "FLOAT"),
                    ("time_logs", "progress_unit", "VARCHAR"),
                    ("sessions", "rest_start_time", "TIMESTAMP"),
                    ("sessions", "save_state_context", "VARCHAR"),
                    ("tasks", "is_focus_today", "BOOLEAN DEFAULT FALSE"),
                    ("projects", "parent_id", "INTEGER REFERENCES projects(id) ON DELETE SET NULL"),
                    ("sessions", "project_id", "INTEGER REFERENCES projects(id) ON DELETE SET NULL"),
                    ("tasks", "project_id", "INTEGER REFERENCES projects(id) ON DELETE SET NULL"),
                    ("time_logs", "project_id", "INTEGER REFERENCES projects(id) ON DELETE SET NULL"),
                ]
                for table, col, col_type in columns_to_add:
                    try:
                        conn.execute(sql_text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}"))
                    except Exception as e:
                        print(f"Migrate {{table}}.{{col}} skipped: {{e}}")                        
    except Exception as e:
        print(f"Migration error: {e}")
    # ---------------------------------------------

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
