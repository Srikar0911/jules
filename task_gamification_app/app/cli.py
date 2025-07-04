import getpass # For securely getting password input
import datetime # Import the datetime module
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
# The duplicated run_cli() and display_main_menu() functions were removed from the SEARCH block
# as they appeared due to a previous file read error.
# Assuming the models import is:
from .models import User, Task, TaskStatus # Ensure TaskStatus is imported

# Global variable to store the current logged-in user's ID (simple session management)
# In a real web app, this would be handled by a proper session mechanism.
CURRENT_USER_ID = None

def get_db_session() -> Session:
    """Helper function to get a new database session."""
    return SessionLocal()

def register_user():
    """Handles new user registration."""
    print("\n--- Register New User ---")
    db = get_db_session()
    try:
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return

        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Username '{username}' already exists. Please choose a different one.")
            return

        password = getpass.getpass("Enter password: ")
        if not password:
            print("Password cannot be empty.")
            return
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Passwords do not match.")
            return

        new_user = User(username=username)
        new_user.set_password(password) # Use the method from the User model
        db.add(new_user)
        db.commit()
        print(f"User '{username}' registered successfully!")
    except Exception as e:
        db.rollback()
        print(f"An error occurred during registration: {e}")
    finally:
        db.close()

def login_user():
    """Handles user login and sets CURRENT_USER_ID."""
    global CURRENT_USER_ID
    print("\n--- User Login ---")
    db = get_db_session()
    try:
        username = input("Enter username: ").strip()
        password = getpass.getpass("Enter password: ")

        user = db.query(User).filter(User.username == username).first()

        if user and user.check_password(password):
            CURRENT_USER_ID = user.id
            print(f"Welcome, {username}! You are now logged in.")
        else:
            CURRENT_USER_ID = None
            print("Invalid username or password.")
    except Exception as e:
        print(f"An error occurred during login: {e}")
    finally:
        db.close()

def logout_user():
    """Logs out the current user."""
    global CURRENT_USER_ID
    if CURRENT_USER_ID is None:
        print("No user is currently logged in.")
        return

    # For CLI, logout is essentially clearing the global user ID
    user_id_to_logout = CURRENT_USER_ID
    CURRENT_USER_ID = None
    # Optionally, retrieve username before clearing for a personalized message
    # db = get_db_session()
    # user = db.query(User).filter(User.id == user_id_to_logout).first()
    # if user:
    #     print(f"User '{user.username}' logged out successfully.")
    # else:
    #     print("Logged out successfully.") # Generic if user not found (should not happen)
    # db.close()
    print("You have been logged out.")


def display_main_menu():
    """Displays the main menu options based on login status."""
    print("\n--- Task Gamification App Menu ---")
    if CURRENT_USER_ID is None:
        print("1. Register")
        print("2. Login")
        print("0. Exit")
    else:
        # Placeholder for logged-in user options
        # db = get_db_session()
        # user = db.query(User).filter(User.id == CURRENT_USER_ID).first()
        # username = user.username if user else "User"
        # db.close()
        # print(f"(Logged in as: {username})") # Would require DB query each time
        print("(Logged In)")
        print("3. Create Task (Not Implemented Yet)")
        print("4. View Tasks (Not Implemented Yet)")
        print("5. Complete Task (Not Implemented Yet)")
        print("6. View Leaderboard (Not Implemented Yet)")
        print("7. Logout")
        print("0. Exit")

def run_cli():
    """Main loop for the CLI application."""
from .models import User, Task, TaskStatus # Ensure TaskStatus is imported

# Global variable to store the current logged-in user's ID (simple session management)
# In a real web app, this would be handled by a proper session mechanism.
CURRENT_USER_ID = None
POINTS_PER_TASK = 10 # Define points for completing a task

# Import service functions
from .services import create_user as create_user_service, verify_user_login as verify_user_login_service

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

    password = getpass.getpass("Enter password: ")
    if not password:
        print("Password cannot be empty.")
        return
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match.")
        return

    db = get_db_session()
# Import service functions and custom exceptions
from .services import (
    create_user as create_user_service,
    verify_user_login as verify_user_login_service,
    UsernameExistsError,
    UserCreationError
)

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
        new_user_obj = create_user_service(db_session=db, username=username, password=password)
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

    db = get_db_session()
    try:
        new_task = Task(description=description, user_id=CURRENT_USER_ID)
        db.add(new_task)
        db.commit()
        print(f"Task '{description}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred while creating the task: {e}")
    finally:
        db.close()

def view_tasks_cli():
    """CLI function for a logged-in user to view their pending tasks."""
    if CURRENT_USER_ID is None:
        print("You must be logged in to view tasks.")
        return

    print("\n--- Your Pending Tasks ---")
    db = get_db_session()
    try:
        tasks = db.query(Task).filter(
            Task.user_id == CURRENT_USER_ID,
            Task.status == TaskStatus.PENDING
        ).order_by(Task.creation_date).all()

        if not tasks:
            print("No pending tasks found.")
        else:
            for task in tasks:
                print(f"  ID: {task.id} | Description: {task.description} | Created: {task.creation_date.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"An error occurred while fetching tasks: {e}")
    finally:
        db.close()

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

    db = get_db_session()
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == CURRENT_USER_ID
        ).first()

        if not task:
            print(f"Task with ID {task_id} not found or does not belong to you.")
            return

        if task.status == TaskStatus.COMPLETED:
            print(f"Task '{task.description}' is already marked as completed.")
            return

        task.status = TaskStatus.COMPLETED
        task.completion_date = datetime.datetime.utcnow() # Import datetime if not already

        # Award points to the user
        user = db.query(User).filter(User.id == CURRENT_USER_ID).first()
        if user:
            user.points += POINTS_PER_TASK # Use the defined constant
            print(f"Task '{task.description}' marked as completed. You earned {POINTS_PER_TASK} points!")
            print(f"Your total points: {user.points}")
        else: # Should not happen if CURRENT_USER_ID is valid
            print(f"Task '{task.description}' marked as completed, but could not update points (user not found).")

        print("DEBUG: About to commit task status change.") # Simplified debug print
        # db.flush() removed
        # print("DEBUG: Flush called.") removed
        db.commit()
        print("DEBUG: Commit called.") # Temporary debug print
    except Exception as e:
        db.rollback()
        print(f"An error occurred while completing the task: {e}")
        raise e # Re-raise the exception for debugging
    finally:
        db.close()


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
        print("6. View Leaderboard (Not Implemented Yet)")
        print("7. Logout")
        print("0. Exit")

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
        # The following block was erroneously duplicated here. It's part of complete_task_cli.
        # else: # Should not happen if CURRENT_USER_ID is valid
        #     print(f"Task '{task.description}' marked as completed, but could not update points (user not found).")
        #
        # db.commit() # This was also part of the erroneous duplication
    # except Exception as e: # This was the line causing SyntaxError due to improper nesting
    #     db.rollback()
    #     print(f"An error occurred while completing the task: {e}")
    # finally:
    #     db.close()

def view_leaderboard_cli():
    """CLI function to display the leaderboard (users sorted by points)."""
    print("\n--- Leaderboard ---")
    db = get_db_session()
    try:
        # Query users, order by points descending, limit to top N if desired (e.g., top 10)
        users = db.query(User).order_by(User.points.desc()).all() # Add .limit(10) for top 10

        if not users:
            print("No users found to display on the leaderboard.")
        else:
            print(f"{'Rank':<5} | {'Username':<20} | {'Points':>10}")
            print("-" * 40)
            for i, user in enumerate(users):
                print(f"{i+1:<5} | {user.username:<20} | {user.points:>10}")
    except Exception as e:
        print(f"An error occurred while fetching the leaderboard: {e}")
    finally:
        db.close()


def display_main_menu():
    """Displays the main menu options based on login status."""
    print("\n--- Task Gamification App Menu ---")
    if CURRENT_USER_ID is None:
        print("1. Register")
        print("2. Login")
        print("0. Exit")
    else:
        print("(Logged In)")
        print("3. Create Task")
        print("4. View My Pending Tasks")
        print("5. Complete Task")
        print("6. View Leaderboard")
        print("7. Logout")
        print("0. Exit")

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
