import os
import sys

# To run this application, the parent directory of 'task_gamification_app'
# must be in the PYTHONPATH. The recommended way to run this is as a module
# from the project root directory (the one containing the task_gamification_app folder):
#
# python -m task_gamification_app.run_web
#
# This ensures all absolute imports like 'from task_gamification_app.webapp import app'
# work correctly.

# The imports are now absolute, consistent with the rest of the application.
from task_gamification_app.webapp import app
from task_gamification_app.app.db import init_db
from task_gamification_app.run_migrations import run_migrations

if __name__ == '__main__':
    print("Initializing database tables (if they don't exist)...")
    try:
        init_db()
        print("Database table initialization check complete.")
    except Exception as e:
        print(f"Error during database table initialization: {e}")
        sys.exit(1)

    print("Running database migrations (if any)...")
    try:
        run_migrations()
        print("Database migrations check complete.")
    except Exception as e:
        print(f"Error during database migrations: {e}")
        print("Please check your database configuration and migration scripts.")
        sys.exit(1) # It's unsafe to continue if migrations fail.

    print("Starting Flask development server...")
    # Debug mode should ideally be controlled by an environment variable for production
    # For example: app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
