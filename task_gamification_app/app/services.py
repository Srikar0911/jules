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

from typing import Optional

def create_task_for_user(db_session: Session, user_id: int, description: str, due_date: Optional[datetime.datetime] = None) -> Task:
    """Creates a new task for a given user, optionally including a due date."""
    new_task = Task(description=description, user_id=user_id, due_date=due_date)
    db_session.add(new_task)
    try:
        db_session.commit()
        db_session.refresh(new_task)
        return new_task
    except SQLAlchemyError as e:
        db_session.rollback()
        raise ServiceError(f"Database error occurred while creating task: {e}")

def update_task_details(db_session: Session, task_id: int, user_id: int, description: Optional[str] = None, due_date: Optional[datetime.datetime] = None, set_due_date_none: bool = False) -> Task:
    """
    Updates a task's description and/or due date.
    `set_due_date_none=True` explicitly sets due_date to None.
    """
    task = db_session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise TaskNotFoundError(f"Task with ID {task_id} not found or does not belong to you.")

    if task.status == TaskStatus.COMPLETED:
        raise ServiceError("Cannot update a completed task.")

    if description is not None:
        task.description = description

    if set_due_date_none:
        task.due_date = None
    elif due_date is not None: # Only update if due_date is explicitly passed and not None
        task.due_date = due_date

    try:
        db_session.commit()
        db_session.refresh(task)
        return task
    except SQLAlchemyError as e:
        db_session.rollback()
        raise ServiceError(f"Database error occurred while updating task: {e}")

def delete_task_for_user(db_session: Session, task_id: int, user_id: int) -> bool:
    """Deletes a task for a given user. Returns True if successful."""
    task = db_session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise TaskNotFoundError(f"Task with ID {task_id} not found or does not belong to you.")

    db_session.delete(task)
    try:
        db_session.commit()
        return True
    except SQLAlchemyError as e:
        db_session.rollback()
        raise ServiceError(f"Database error occurred while deleting task: {e}")

def get_tasks_for_user(
    db_session: Session,
    user_id: int,
    status: Optional[TaskStatus] = None,
    sort_by: str = "creation_date",
    description: Optional[str] = None,
    creation_date: Optional[datetime.date] = None,
    due_date: Optional[datetime.date] = None,
    completion_date: Optional[datetime.date] = None
) -> List[Task]:
    """
    Retrieves tasks for a given user, with extensive filtering and sorting.
    """
    query = db_session.query(Task).filter(Task.user_id == user_id)

    # Apply filters
    if description:
        query = query.filter(Task.description.ilike(f'%{description}%'))
    if status:
        query = query.filter(Task.status == status)
    if creation_date:
        query = query.filter(func.date(Task.creation_date) == creation_date)
    if due_date:
        query = query.filter(func.date(Task.due_date) == due_date)
    if completion_date:
        query = query.filter(func.date(Task.completion_date) == completion_date)

    # Apply sorting
    if sort_by == "due_date":
        query = query.order_by(Task.due_date.asc().nullslast(), Task.creation_date.desc())
    else:  # Default sort by creation_date
        query = query.order_by(Task.creation_date.desc())

    return query.all()

# Removed get_pending_tasks_for_user as get_tasks_for_user covers its functionality by passing status=TaskStatus.PENDING

def complete_task(db_session: Session, task_id: int, user_id: int) -> Task:
    """Marks a task as completed and awards points to the user."""
    # Ensure task is fetched for update, preventing race conditions if points were critical
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

from sqlalchemy import func # For aggregate functions like count and rank

# Structure for leaderboard entry (conceptual, actual return is list of dicts/rows)
# class LeaderboardEntry:
#     user_id: int
#     username: str
#     points: int
#     rank: int
#     completed_tasks_count: int

def get_leaderboard_users_paginated(db_session: Session, page: int = 1, per_page: int = 10) -> tuple[List[dict], int]:
    """
    Retrieves users for the leaderboard with rank and completed task count, paginated.
    Returns a list of dictionaries (each representing a leaderboard entry) and the total number of users.
    """
    offset = (page - 1) * per_page

    # Subquery to count completed tasks for each user
    completed_tasks_subquery = (
        db_session.query(
            Task.user_id,
            func.count(Task.id).label("completed_tasks_count")
        )
        .filter(Task.status == TaskStatus.COMPLETED)
        .group_by(Task.user_id)
        .subquery('completed_tasks_sq') # Alias for the subquery
    )

    # Main query to join User details with rank and completed tasks count
    # Using DENSE_RANK() window function to assign ranks based on points
    query = (
        db_session.query(
            User.id.label("user_id"),
            User.username,
            User.points,
            func.dense_rank().over(order_by=User.points.desc()).label("rank"),
            func.coalesce(completed_tasks_subquery.c.completed_tasks_count, 0).label("completed_tasks_count")
        )
        .select_from(User) # Explicitly select from User table first
        .outerjoin( # Use outerjoin to include users with no completed tasks
            completed_tasks_subquery,
            User.id == completed_tasks_subquery.c.user_id
        )
        .order_by(func.dense_rank().over(order_by=User.points.desc()).asc(), User.id.asc()) # Order by rank, then by ID for tie-breaking
    )

    total_users_count = query.count() # Get total count before applying limit/offset

    paginated_results = query.limit(per_page).offset(offset).all()

    leaderboard_entries = [
        {
            "user_id": row.user_id,
            "username": row.username,
            "points": row.points,
            "rank": row.rank,
            "completed_tasks_count": row.completed_tasks_count
        }
        for row in paginated_results
    ]

    return leaderboard_entries, total_users_count

# Deprecate or remove the old get_leaderboard_users if this new one is preferred.
# For now, I'll leave it and the route will call the new one.
# def get_leaderboard_users(db_session: Session, limit: int = 10) -> List[User]:
#     """Retrieves users for the leaderboard, sorted by points."""
#     return db_session.query(User).order_by(User.points.desc()).limit(limit).all()
