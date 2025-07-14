import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Adjust the import path to find the app modules
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import datetime
from task_gamification_app.app.models import Base, User, Task, TaskStatus
from task_gamification_app.app.services import (
    create_user,
    verify_user_login,
    UsernameExistsError,
    UserCreationError,
    create_task_for_user,
    get_tasks_for_user,
    complete_task
)

class BaseServiceTest(unittest.TestCase):
    """
    Base class for service tests that sets up a transactional in-memory DB.
    This pattern ensures that each test runs in isolation.
    """

    @classmethod
    def setUpClass(cls):
        """Create an in-memory DB engine and tables once for the class."""
        cls.engine = create_engine(
            'sqlite:///:memory:',
            # Using StaticPool is recommended for in-memory SQLite to ensure
            # all sessions use the same single connection.
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        # Create a sessionmaker that will be used to create sessions
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        """
        For each test, create a new session and wrap it in a transaction.
        The transaction will be rolled back in tearDown.
        """
        # This is the "transactional" part of the test setup
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        self.session = self.Session(bind=self.connection)

    def tearDown(self):
        """
        Roll back the transaction and close the connection after each test.
        This ensures tests are isolated from each other.
        """
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    @classmethod
    def tearDownClass(cls):
        """Drop all tables after all tests in the class have run."""
        Base.metadata.drop_all(cls.engine)


class TestUserServices(BaseServiceTest):
    def test_create_user_success(self):
        """Test successful user creation."""
        user = create_user(self.session, "test_first", "test_last", "testuser", "test@example.com", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_user_duplicate_username(self):
        """Test that creating a user with a duplicate username raises an error."""
        create_user(self.session, "test_first", "test_last", "testuser", "test@example.com", "password123")
        with self.assertRaises(UsernameExistsError):
            create_user(self.session, "test_first", "test_last", "testuser", "test2@example.com", "anotherpassword")

    def test_create_user_duplicate_email(self):
        """Test that creating a user with a duplicate email raises an error."""
        create_user(self.session, "test_first", "test_last", "testuser1", "test@example.com", "password123")
        with self.assertRaises(UserCreationError): # The service raises UserCreationError for duplicate email
            create_user(self.session, "test_first", "test_last", "testuser2", "test@example.com", "anotherpassword")


class TestTaskServices(BaseServiceTest):
    def setUp(self):
        """
        Extend the base setUp to create a user for task-related tests.
        """
        super().setUp() # This sets up the connection, transaction, and session
        self.user = create_user(self.session, "test_first", "test_last", "testuser", "test@example.com", "password123")
        # The user created here will be rolled back after the test.

    def test_filter_tasks(self):
        """Test filtering tasks by different criteria."""
        task1 = create_task_for_user(self.session, self.user.id, "Test task 1", due_date=datetime.date(2024, 1, 1))
        task2 = create_task_for_user(self.session, self.user.id, "Another task 2", due_date=datetime.date(2024, 1, 2))
        complete_task(self.session, task2.id, self.user.id)

        # Filter by description
        tasks = get_tasks_for_user(self.session, self.user.id, description="Test")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, task1.id)

        # Filter by status
        tasks = get_tasks_for_user(self.session, self.user.id, status=TaskStatus.COMPLETED)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, task2.id)

        # Filter by due date
        tasks = get_tasks_for_user(self.session, self.user.id, due_date=datetime.date(2024, 1, 1))
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, task1.id)

        # Filter by creation date
        tasks = get_tasks_for_user(self.session, self.user.id, creation_date=datetime.date.today())
        self.assertEqual(len(tasks), 2)

        # Filter by completion date
        tasks = get_tasks_for_user(self.session, self.user.id, completion_date=datetime.date.today())
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, task2.id)


if __name__ == '__main__':
    unittest.main()