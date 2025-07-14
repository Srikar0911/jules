import os
import importlib.util
from sqlalchemy import create_engine, inspect, Table, MetaData, Column, String
from alembic.operations import Operations
from alembic.migration import MigrationContext

DATABASE_URL = "sqlite:///./task_gamification.db"
MIGRATIONS_DIR = "task_gamification_app/app/migrations/versions"

def get_migration_files():
    """Returns a sorted list of migration files."""
    files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".py") and f != "__init__.py"]
    return sorted(files)

def run_migrations():
    """Runs all pending migrations."""
    engine = create_engine(DATABASE_URL)

    # Add this import
    from app.models import Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)

    inspector = inspect(engine)

    # Get the list of all migration files
    migration_files = get_migration_files()

    # Get the list of migrations that have already been run
    # For simplicity, we'll store the ran migrations in a table.
    # If the table doesn't exist, create it.
    meta = MetaData()
    if not inspector.has_table("alembic_version"):
        alembic_version = Table(
            "alembic_version",
            meta,
            Column("version_num", String(32), primary_key=True),
        )
        alembic_version.create(engine)

    with engine.connect() as connection:
        from sqlalchemy import text
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        ran_migrations = {row[0] for row in result}

    for migration_file in migration_files:
        migration_name = os.path.splitext(migration_file)[0]
        if migration_name not in ran_migrations:
            print(f"Running migration: {migration_name}")
            spec = importlib.util.spec_from_file_location(migration_name, os.path.join(MIGRATIONS_DIR, migration_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.upgrade(op)
            with engine.connect() as connection:
                from sqlalchemy import text
                connection.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{migration_name}')"))
            print(f"Migration {migration_name} complete.")

if __name__ == "__main__":
    run_migrations()
