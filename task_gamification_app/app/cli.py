import getpass # For securely getting password input
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User

# Global variable to store the current logged-in user's ID (simple session management)
# In a real web app, this would be handled by a proper session mechanism.
CURRENT_USER_ID = None

# Import service functions and custom exceptions
from .services import (
    create_user as create_user_service,
    verify_user_login as verify_user_login_service,
    create_task_for_user,
    get_tasks_for_user,
    complete_task,
    get_leaderboard_users_paginated, # Use the new paginated and more detailed function
    POINTS_PER_TASK,
    UsernameExistsError,
    UserCreationError,
    TaskNotFoundError,
    TaskCompletionError,
    ServiceError
)
from .models import TaskStatus # Import TaskStatus for filtering

def get_db_session() -> Session:
    """Helper function to get a new database session."""
    return SessionLocal()

def register_user():
    """Handles new user registration using the user service."""
    print("\n--- Register New User ---")
    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    email = input("Enter email: ").strip()
    if not email:
        print("Email cannot be empty.")
        return

    password = getpass.getpass("Enter password: ")
    if not password:
        print("Password cannot be empty.")
        return
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match.")
        return

    db = get_db_session()
    try:
        new_user_obj = create_user_service(db_session=db, username=username, email=email, password=password)
        print(f"User '{new_user_obj.username}' registered successfully!")
    except UsernameExistsError:
        print(f"Username '{username}' already exists. Please choose a different one.")
    except UserCreationError as e:
        print(f"Could not register user due to a database or unexpected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during registration: {e}")
    finally:
        db.close()

def login_user():
    """Handles user login using the user service and sets CURRENT_USER_ID."""
    global CURRENT_USER_ID
    print("\n--- User Login ---")
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")

    db = get_db_session()
    try:
        # Use the service function to verify login
        user_obj = verify_user_login_service(db_session=db, username=username, password=password)
        if user_obj:
            CURRENT_USER_ID = user_obj.id
            print(f"Welcome, {username}! You are now logged in.")
        else:
            CURRENT_USER_ID = None
            print("Invalid username or password.")
    except Exception as e:
        # This generic catch is less likely if services.py handles its own DB exceptions
        print(f"An unexpected error occurred during login: {e}")
    finally:
        db.close()

def logout_user():
    """Logs out the current user."""
    global CURRENT_USER_ID
    if CURRENT_USER_ID is None:
        print("No user is currently logged in.")
        return

    CURRENT_USER_ID = None
    print("You have been logged out.")

def create_task_cli():
    """CLI function for a logged-in user to create a new task."""
    if CURRENT_USER_ID is None:
        print("You must be logged in to create a task.")
        return

    print("\n--- Create New Task ---")
    description = input("Enter task description: ").strip()
    if not description:
        print("Task description cannot be empty.")
        return

    db_session = get_db_session()
    try:
        create_task_for_user(db_session=db_session, user_id=CURRENT_USER_ID, description=description)
        print(f"Task '{description}' created successfully.")
    except ServiceError as e:
        print(f"An error occurred while creating the task: {e}")
    finally:
        db_session.close()

def view_tasks_cli():
    """CLI function for a logged-in user to view their pending tasks."""
    if CURRENT_USER_ID is None:
        print("You must be logged in to view tasks.")
        return

    print("\n--- Your Pending Tasks ---")
    db_session = get_db_session()
    try:
        # Use the more generic get_tasks_for_user with a specific status
        tasks = get_tasks_for_user(db_session=db_session, user_id=CURRENT_USER_ID, status=TaskStatus.PENDING)
        if not tasks:
            print("No pending tasks found.")
        else:
            for task in tasks:
                due_date_str = f" | Due: {task.due_date.strftime('%Y-%m-%d')}" if task.due_date else ""
                print(f"  ID: {task.id} | Description: {task.description} | Created: {task.creation_date.strftime('%Y-%m-%d %H:%M')}{due_date_str}")
    except ServiceError as e:
        print(f"An error occurred while fetching tasks: {e}")
    finally:
        db_session.close()

def complete_task_cli():
    """CLI function for a logged-in user to mark a task as completed and earn points."""
    if CURRENT_USER_ID is None:
        print("You must be logged in to complete a task.")
        return

    print("\n--- Complete Task ---")
    try:
        task_id_str = input("Enter the ID of the task to complete: ").strip()
        if not task_id_str.isdigit():
            print("Invalid task ID format. Please enter a number.")
            return
        task_id = int(task_id_str)
    except ValueError:
        print("Invalid task ID. Please enter a number.")
        return

    db_session = get_db_session()
    try:
        completed_task = complete_task(db_session=db_session, task_id=task_id, user_id=CURRENT_USER_ID)
        # We need the user's latest points total
        user = db_session.query(User).filter(User.id == CURRENT_USER_ID).first()
        print(f"Task '{completed_task.description}' marked as completed. You earned {POINTS_PER_TASK} points!")
        if user:
            print(f"Your total points: {user.points}")
    except (TaskNotFoundError, TaskCompletionError, ServiceError) as e:
        print(f"An error occurred while completing the task: {e}")
    finally:
        db_session.close()


def display_main_menu():
    """Displays the main menu options based on login status."""
    print("\n--- Task Gamification App Menu ---")
    if CURRENT_USER_ID is None:
        print("1. Register")
        print("2. Login")
        print("0. Exit")
    else:
        # Display username if logged in
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == CURRENT_USER_ID).first()
            username = user.username if user else "Unknown User"
            print(f"(Logged in as: {username})")
        finally:
            db.close()

        print("3. Create Task")
        print("4. View My Pending Tasks")
        print("5. Complete Task")
        print("6. View Leaderboard")
        print("7. Logout")
        print("0. Exit")

def view_leaderboard_cli():
    """CLI function to display the leaderboard (users sorted by points)."""
    print("\n--- Leaderboard ---")
    db_session = get_db_session()
    try:
        # Fetch the top 10 users for the CLI view (first page)
        leaderboard_entries, _ = get_leaderboard_users_paginated(db_session=db_session, page=1, per_page=10)
        if not leaderboard_entries:
            print("No users found to display on the leaderboard.")
        else:
            # Updated header to include new information
            print(f"{'Rank':<5} | {'Username':<20} | {'Points':>10} | {'Tasks Completed':>15}")
            print("-" * 65)
            for entry in leaderboard_entries:
                # The rank is now provided directly by the service function
                print(f"{entry['rank']:<5} | {entry['username']:<20} | {entry['points']:>10} | {entry['completed_tasks_count']:>15}")
    except ServiceError as e:
        print(f"An error occurred while fetching the leaderboard: {e}")
    finally:
        db_session.close()

def run_cli():
    """Main loop for the CLI application."""
    while True:
        display_main_menu()
        choice = input("Enter your choice: ").strip()

        if CURRENT_USER_ID is None: # Logged-out state
            if choice == '1':
                register_user()
            elif choice == '2':
                login_user()
            elif choice == '0':
                print("Exiting application.")
                break
            else:
                print("Invalid choice. Please try again.")
        else: # Logged-in state
            if choice == '3':
                create_task_cli()
            elif choice == '4':
                view_tasks_cli()
            elif choice == '5':
                complete_task_cli()
            elif choice == '6':
                view_leaderboard_cli()
            elif choice == '7':
                logout_user()
            elif choice == '0':
                print("Exiting application.")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # This allows running cli.py directly for testing CLI features
    print("Starting CLI directly...")
    # It's good practice to ensure DB is initialized before CLI runs
    # init_db() # Ensure tables are created
    # However, if main.py is the entry point, it should handle init_db()

    # For direct CLI testing, ensure db is initialized:
    # from app.db import init_db # Local import for direct run
    # init_db()

    run_cli()
