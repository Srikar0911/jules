import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    create_task_for_user,
    get_tasks_for_user,
    complete_task
)

class TestUserServices(unittest.TestCase):

    def setUp(self):
        """Set up a temporary in-memory database for each test."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        """Clean up the database after each test."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_user_success(self):
        """Test successful user creation."""
        user = create_user(self.session, "testuser", "test@example.com", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_user_duplicate_username(self):
        """Test that creating a user with a duplicate username raises an error."""
        create_user(self.session, "testuser", "test@example.com", "password123")
        with self.assertRaises(UsernameExistsError):
            create_user(self.session, "testuser", "test2@example.com", "anotherpassword")


class TestTaskServices(unittest.TestCase):

    def setUp(self):
        """Set up a temporary in-memory database for each test."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.user = create_user(self.session, "testuser", "test@example.com", "password123")

    def tearDown(self):
        """Clean up the database after each test."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

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