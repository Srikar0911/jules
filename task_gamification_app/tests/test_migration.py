import unittest
from sqlalchemy import create_engine, inspect
from task_gamification_app.app.models import Base

class TestMigration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_due_date_column_exists(self):
        """
        Tests that the due_date column exists in the tasks table.
        """
        inspector = inspect(self.engine)
        columns = [column['name'] for column in inspector.get_columns('tasks')]
        self.assertIn('due_date', columns)

    def test_email_column_exists(self):
        """
        Tests that the email column exists in the users table.
        """
        inspector = inspect(self.engine)
        columns = [column['name'] for column in inspector.get_columns('users')]
        self.assertIn('email', columns)

if __name__ == '__main__':
    unittest.main()
