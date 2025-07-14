import unittest
from unittest.mock import patch, call
import os
import sys

# Add the project root to the Python path to allow importing app modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the module itself to access its globals directly like app.cli.CURRENT_USER_ID
import app.cli
# Specific functions can still be imported for direct calling if preferred
from app.cli import register_user, login_user, create_task_cli, complete_task_cli, logout_user
from app.models import User, Task, TaskStatus
from app.db import SessionLocal, init_db, Base, engine

class TestCliFunctions(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        # Reset app.cli.CURRENT_USER_ID before each test
        app.cli.CURRENT_USER_ID = None

    def tearDown(self):
        """Clean up the database and session after each test."""
        self.db.close()
        Base.metadata.drop_all(bind=engine)
        # Reset app.cli.CURRENT_USER_ID after each test
        app.cli.CURRENT_USER_ID = None


    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_register_user_success(self, mock_input, mock_getpass):
        """Test successful user registration."""
        mock_input.side_effect = ["test_first", "test_last", "testuser_reg", "test@example.com", "testpass123", "testpass123"]
        mock_getpass.return_value = "testpass123"

        # Suppress print output during test
        with patch('builtins.print') as mock_print:
            register_user()

        user = self.db.query(User).filter(User.username == "testuser_reg").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser_reg")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_register_user_username_exists(self, mock_input, mock_getpass):
        """Test registration when username already exists."""
        # First, create a user
        existing_user = User(first_name="test", last_name="test", username="existinguser", email="test@example.com")
        existing_user.set_password("oldpass")
        self.db.add(existing_user)
        self.db.commit()

        mock_input.side_effect = ["test_first", "test_last", "existinguser", "new@example.com", "newpass123", "newpass123"] # Attempt to register same username
        mock_getpass.return_value = "newpass123"

        with patch('builtins.print') as mock_print:
            register_user()

        mock_print.assert_any_call("Username 'existinguser' already exists. Please choose a different one.")
        user_count = self.db.query(User).filter(User.username == "existinguser").count()
        self.assertEqual(user_count, 1) # Should still be only one user with this name

    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_register_user_password_mismatch(self, mock_input, mock_getpass):
        """Test registration with mismatched passwords."""
        mock_input.side_effect = ["mismatchuser", "test@example.com", "pass1", "pass2"]
        # mock_getpass needs to be called twice for password and confirm_password
        mock_getpass.side_effect = ["pass1", "pass2"]


        with patch('builtins.print') as mock_print:
            register_user()

        mock_print.assert_any_call("Passwords do not match.")
        user = self.db.query(User).filter(User.username == "mismatchuser").first()
        self.assertIsNone(user) # User should not be created

    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_login_user_success(self, mock_input, mock_getpass):
        """Test successful user login."""
        # Setup: Create a user to log in with
        user = User(first_name="test", last_name="test", username="loginuser", email="test@example.com")
        user.set_password("loginpass")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user) # Ensure user.id is available

        mock_input.return_value = "loginuser"  # Simulates typing username
        mock_getpass.return_value = "loginpass" # Simulates typing password

        with patch('builtins.print') as mock_print:
            login_user() # This function should modify app.cli.CURRENT_USER_ID

        self.assertEqual(app.cli.CURRENT_USER_ID, user.id) # Check the module's global
        mock_print.assert_any_call("Welcome, loginuser! You are now logged in.")

    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_login_user_failure_wrong_password(self, mock_input, mock_getpass):
        """Test login failure with wrong password."""
        # Setup: Create a user
        user = User(first_name="test", last_name="test", username="loginuser2", email="test@example.com")
        user.set_password("correctpass")
        self.db.add(user)
        self.db.commit()

        mock_input.return_value = "loginuser2"
        mock_getpass.return_value = "wrongpass" # Simulate wrong password

        with patch('builtins.print') as mock_print:
            login_user()

        self.assertIsNone(app.cli.CURRENT_USER_ID) # Check the module's global
        mock_print.assert_any_call("Invalid username or password.")

    @patch('app.cli.getpass.getpass')
    @patch('builtins.input')
    def test_login_user_failure_nonexistent_user(self, mock_input, mock_getpass):
        """Test login failure with a username that doesn't exist."""
        mock_input.return_value = "nonexistentuser"
        mock_getpass.return_value = "anypass"

        with patch('builtins.print') as mock_print:
            login_user()

        self.assertIsNone(app.cli.CURRENT_USER_ID) # Check the module's global
        mock_print.assert_any_call("Invalid username or password.")

    def test_logout_user(self):
        """Test user logout."""
        app.cli.CURRENT_USER_ID = 1 # Simulate a logged-in user by setting the module's global

        with patch('builtins.print') as mock_print:
            logout_user() # This function should modify app.cli.CURRENT_USER_ID

        self.assertIsNone(app.cli.CURRENT_USER_ID) # Check the module's global
        mock_print.assert_any_call("You have been logged out.")

    def test_logout_user_not_logged_in(self):
        """Test logout when no user is logged in."""
        app.cli.CURRENT_USER_ID = None # Ensure no one is logged in (in the module's global)

        with patch('builtins.print') as mock_print:
            logout_user()

        self.assertIsNone(app.cli.CURRENT_USER_ID) # Check the module's global
        mock_print.assert_any_call("No user is currently logged in.")

    @patch('builtins.input')
    def test_create_task_cli_success(self, mock_input):
        """Test successful task creation by a logged-in user."""
        # Setup: Create a user
        user = User(first_name="test", last_name="test", username="taskuser", email="test@example.com")
        user.set_password("taskpass")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user) # Ensure user.id is loaded

        mock_input.return_value = "New test task" # Simulate task description input

        # Patch CURRENT_USER_ID directly in the app.cli module for this test
        with patch('app.cli.CURRENT_USER_ID', user.id):
            with patch('builtins.print') as mock_print:
                create_task_cli()

        task = self.db.query(Task).filter(Task.description == "New test task", Task.user_id == user.id).first()
        self.assertIsNotNone(task)
        if task: # Avoid AttributeError if task is None
            self.assertEqual(task.status, TaskStatus.PENDING)
        mock_print.assert_any_call("Task 'New test task' created successfully.")

    @patch('builtins.input')
    def test_create_task_cli_not_logged_in(self, mock_input):
        """Test create task when no user is logged in."""
        global CURRENT_USER_ID
        CURRENT_USER_ID = None # Ensure no one is logged in

        mock_input.return_value = "Should not be created"
        with patch('builtins.print') as mock_print:
            create_task_cli()

        mock_print.assert_any_call("You must be logged in to create a task.")
        task_count = self.db.query(Task).count()
        self.assertEqual(task_count, 0) # No task should be created

    @patch('builtins.input')
    def test_complete_task_cli_success(self, mock_input):
        """Test successful task completion."""
        user = User(first_name="test", last_name="test", username="taskcompleter", email="test@example.com", points=0)
        user.set_password("completerpass")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        task_to_complete = Task(description="Task to complete", user_id=user.id, status=TaskStatus.PENDING)
        self.db.add(task_to_complete)
        self.db.commit()
        self.db.refresh(task_to_complete)
        task_id = task_to_complete.id # Store id before potentially stale object

        mock_input.return_value = str(task_id)

        with patch('app.cli.CURRENT_USER_ID', user.id):
            complete_task_cli()

        self.db.commit()

        # Re-query the task and user from the database to get the freshest state
        updated_task = self.db.query(Task).filter(Task.id == task_id).first()
        updated_user = self.db.query(User).filter(User.id == user.id).first()

        self.assertIsNotNone(updated_task, "Task should exist after trying to complete it.")
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)

        if updated_task.status == TaskStatus.COMPLETED:
            self.assertIsNotNone(updated_task.completion_date)
            self.assertIsNotNone(updated_user, "User should exist.")
            self.assertEqual(updated_user.points, 10)


    @patch('builtins.input')
    def test_complete_task_cli_not_logged_in(self, mock_input):
        """Test complete task when no user is logged in."""
        global CURRENT_USER_ID
        CURRENT_USER_ID = None

        # Setup a task (though it shouldn't be completable)
        user = User(first_name="test", last_name="test", username="dummyowner", email="test@example.com")
        user.set_password("dummypass")
        self.db.add(user)
        self.db.commit()
        task = Task(description="Dummy task", user_id=user.id)
        self.db.add(task)
        self.db.commit()

        mock_input.return_value = str(task.id)
        with patch('builtins.print') as mock_print:
            complete_task_cli()

        mock_print.assert_any_call("You must be logged in to complete a task.")
        self.db.refresh(task)
        self.assertEqual(task.status, TaskStatus.PENDING) # Task should remain pending


if __name__ == '__main__':
    unittest.main()
