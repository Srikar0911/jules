import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust the import path to find the app modules
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from task_gamification_app.app.models import Base, User
from task_gamification_app.app.services import (
    create_user,
    verify_user_login,
    UsernameExistsError
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
        user = create_user(self.session, "testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("password123"))

    def test_create_user_duplicate_username(self):
        """Test that creating a user with a duplicate username raises an error."""
        create_user(self.session, "testuser", "password123")
        with self.assertRaises(UsernameExistsError):
            create_user(self.session, "testuser", "anotherpassword")

if __name__ == '__main__':
    unittest.main()