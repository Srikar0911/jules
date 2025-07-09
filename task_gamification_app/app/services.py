from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, List # Import Union and List
import datetime
from .models import User, Task, TaskStatus

# Constants
POINTS_PER_TASK = 10 # Define points for completing a task
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

class TaskNotFoundError(ServiceError):
    """Raised when a task is not found or doesn't belong to the user."""
    pass

class TaskCompletionError(ServiceError):
    """Raised for errors during task completion."""
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


def verify_user_login(db_session: Session, username: str, password: str) -> Union[User, None]:
    """
    Verifies user credentials.
    Returns the User object if login is successful, None otherwise.
    """
    user = db_session.query(User).filter(User.username == username).first()
    if user and user.check_password(password):
        return user
    return None

def create_task_for_user(db_session: Session, user_id: int, description: str) -> Task:
    """Creates a new task for a given user."""
    new_task = Task(description=description, user_id=user_id)
    db_session.add(new_task)
    try:
        db_session.commit()
        db_session.refresh(new_task)
        return new_task
    except SQLAlchemyError as e:
        db_session.rollback()
        raise ServiceError(f"Database error occurred while creating task: {e}")

def get_pending_tasks_for_user(db_session: Session, user_id: int) -> List[Task]:
    """Retrieves all pending tasks for a given user."""
    return db_session.query(Task).filter(
        Task.user_id == user_id,
        Task.status == TaskStatus.PENDING
    ).order_by(Task.creation_date).all()

def complete_task(db_session: Session, task_id: int, user_id: int) -> Task:
    """Marks a task as completed and awards points to the user."""
    task = db_session.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

    if not task:
        raise TaskNotFoundError(f"Task with ID {task_id} not found or does not belong to you.")

    if task.status == TaskStatus.COMPLETED:
        # Not an error, but the task is already done. We can return it as is.
        return task

    task.status = TaskStatus.COMPLETED
    task.completion_date = datetime.datetime.utcnow()

    # Award points to the user
    user = db_session.query(User).filter(User.id == user_id).first()
    if user:
        user.points += POINTS_PER_TASK
    
    try:
        db_session.commit()
        db_session.refresh(task)
        return task
    except SQLAlchemyError as e:
        db_session.rollback()
        raise TaskCompletionError(f"Database error occurred while completing task: {e}")

def get_leaderboard_users(db_session: Session, limit: int = 10) -> List[User]:
    """Retrieves users for the leaderboard, sorted by points."""
    return db_session.query(User).order_by(User.points.desc()).limit(limit).all()
