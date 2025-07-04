from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import User

# Custom Exceptions for the service layer
class ServiceError(Exception):
    """Base class for service layer exceptions."""
    pass

class UsernameExistsError(ServiceError):
    """Raised when trying to create a user with an existing username."""
    pass

class UserCreationError(ServiceError):
    """Raised for other errors during user creation."""
    pass

def create_user(db_session: Session, username: str, password: str) -> User:
    """
    Creates a new user, hashes their password, and saves them to the database.
    Returns the User object if successful.
    Raises UsernameExistsError if username is taken.
    Raises UserCreationError for other database issues.
    """
    existing_user = db_session.query(User).filter(User.username == username).first()
    if existing_user:
        raise UsernameExistsError(f"Username '{username}' already exists.")

    new_user = User(username=username)
    new_user.set_password(password)
    db_session.add(new_user)
    try:
        db_session.commit()
        db_session.refresh(new_user)
        return new_user
    except SQLAlchemyError as e: # Catch specific SQLAlchemy errors
        db_session.rollback()
        # Log error e here if logging is set up
        raise UserCreationError(f"Database error occurred during user creation: {e}")
    except Exception as e: # Catch any other unexpected errors
        db_session.rollback()
        # Log error e here
        raise UserCreationError(f"An unexpected error occurred during user creation: {e}")


def verify_user_login(db_session: Session, username: str, password: str) -> User | None:
    """
    Verifies user credentials.
    Returns the User object if login is successful, None otherwise.
    """
    user = db_session.query(User).filter(User.username == username).first()
    if user and user.check_password(password):
        return user
    return None

# We can add more service functions here later for tasks, etc.
# For example:
# def create_task_for_user(db_session: Session, user_id: int, description: str) -> Task | None: ...
# def get_tasks_for_user(db_session: Session, user_id: int) -> list[Task]: ...
# def complete_task_for_user(db_session: Session, task_id: int, user_id: int) -> Task | None: ...
# def get_leaderboard_users(db_session: Session, limit: int = 10) -> list[User]: ...

# Note: Error handling here is basic (returning None).
# In a more complex app, custom exceptions or more detailed error objects might be better.
