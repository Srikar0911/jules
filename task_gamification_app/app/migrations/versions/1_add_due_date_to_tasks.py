from sqlalchemy import Table, Column, DateTime, MetaData
from task_gamification_app.app.db import engine

def upgrade():
    """Adds the due_date column to the tasks table."""
    meta = MetaData()
    tasks = Table('tasks', meta, autoload_with=engine)

    # Check if the column already exists
    if 'due_date' not in [c.name for c in tasks.columns]:
        print("Adding due_date column to tasks table...")
        # Define the column to be added
        col = Column('due_date', DateTime, nullable=True)

        # Build the ALTER TABLE statement
        # This is a simplified way; a more robust solution would use Alembic
        # For SQLite, ALTER TABLE is limited, but adding a column is supported.
        col_name = col.compile(dialect=engine.dialect)
        col_type = col.type.compile(engine.dialect)
        engine.execute(f'ALTER TABLE tasks ADD COLUMN {col_name} {col_type}')
        print("Column due_date added successfully.")
    else:
        print("Column due_date already exists.")

def downgrade():
    """Removes the due_date column from the tasks table."""
    meta = MetaData()
    # In SQLite, dropping columns is not directly supported.
    # A common workaround is to create a new table, copy data, and rename.
    # For this project, we'll keep it simple and just print a message.
    print("Downgrade not implemented for SQLite due to its limitations.")
    # A full migration tool like Alembic would handle this more gracefully.

if __name__ == "__main__":
    print("Running migration to add due_date column...")
    upgrade()
    print("Migration complete.")
