import unittest
from sqlalchemy import create_engine, inspect

class TestMigration(unittest.TestCase):
    def test_due_date_column_exists(self):
        """
        Tests that the due_date column exists in the tasks table.
        """
        engine = create_engine("sqlite:///./task_gamification.db")
        inspector = inspect(engine)
        columns = [column['name'] for column in inspector.get_columns('tasks')]
        self.assertIn('due_date', columns)

if __name__ == '__main__':
    unittest.main()
