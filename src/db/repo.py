import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

# Load environment variables
load_dotenv()

# Get DB URL, fallback to local sqlite if not found
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

# Create engine
# echo=True will print the generated SQL to the console for learning/debugging
engine = create_engine(DATABASE_URL, echo=True)

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
