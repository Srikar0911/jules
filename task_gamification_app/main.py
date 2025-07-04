from app.db import init_db, SessionLocal
from app.models import User, Task # Import models to ensure they are registered with Base

def main():
    print("Initializing Task Gamification App...")
    init_db() # Initialize database and create tables

    # Example: You can add a simple CLI interaction loop here later
    # For now, let's just confirm DB initialization and perhaps add a test user.
    print("Application initialized.")

    # Basic test: Add a user if none exist (optional, for early testing)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("No users found. Consider adding a bootstrap script or admin user creation.")
        else:
            print(f"Found {user_count} user(s) in the database.")

        task_count = db.query(Task).count()
        print(f"Found {task_count} task(s) in the database.")

    finally:
        db.close()

    print("To start the CLI (once implemented), you would run a function from app.cli here.")
    print("Exiting application.")


if __name__ == "__main__":
    main()
