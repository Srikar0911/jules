from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .models import Base # Import Base from models.py

DATABASE_URL = "sqlite:///./task_gamification.db"

engine = create_engine(
    DATABASE_URL,
    # connect_args={"check_same_thread": False} # Needed only for SQLite if using threads, e.g. in FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session (useful for web frameworks like FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    # This will create all tables defined in models.py that inherit from Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created (if they didn't exist).")

if __name__ == "__main__":
    # This script can be run directly to initialize the database.
    print(f"Initializing database at {DATABASE_URL}...")
    init_db()
    print("Database initialization process complete.")

    # Example: Test creating a session (optional, for quick verification)
    # from .models import User # To avoid circular import if models.py also runs db init
    # db = SessionLocal()
    # if db:
    #     print("Successfully created a database session.")
    #     # You could add a test query here if models are fully defined
    #     # and you want to ensure the connection works.
    #     # For example, to see if the users table exists (after init_db()):
    #     # from sqlalchemy import inspect
    #     # inspector = inspect(engine)
    #     # print(f"Tables found: {inspector.get_table_names()}")
    #     db.close()
    # else:
    #     print("Failed to create a database session.")
