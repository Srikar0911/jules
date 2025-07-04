import os
import sys

# Add the project root to sys.path if run_web.py is in the root
# This ensures that 'from task_gamification_app.webapp import app' works correctly
# and also that task_gamification_app.app.db can be found by webapp.
# If run_web.py is inside task_gamification_app, this might need adjustment
# or be unnecessary if task_gamification_app is already in PYTHONPATH.

# Assuming run_web.py is in the PARENT of task_gamification_app (e.g. repo root)
# and task_gamification_app is the main package.
# If task_gamification_app is the root, then imports would be 'from webapp import app'
# The current structure has task_gamification_app as the root folder containing app/ and webapp/

# To make 'from task_gamification_app.webapp import app' work when run_web.py is inside task_gamification_app folder:
# We need the parent of task_gamification_app to be in path, or run with python -m task_gamification_app.run_web
# For simplicity, let's assume task_gamification_app is directly runnable / on path
# or this script is run from the directory *containing* task_gamification_app.

# Let's adjust for running from within the task_gamification_app directory as the current CWD.
# This means task_gamification_app itself is the top-level entity for these imports.

try:
    from webapp import app  # Imports the app instance from webapp/__init__.py
    from app.db import init_db
except ImportError as e:
    print(f"ImportError: {e}")
    print("Please ensure that the script is run from the 'task_gamification_app' directory,")
    print("or that the 'task_gamification_app' directory is in your PYTHONPATH.")
    print("Current sys.path:", sys.path)
    sys.exit(1)


if __name__ == '__main__':
    print("Initializing database (if needed)...")
    try:
        init_db() # Create database tables if they don't exist
        print("Database initialization check complete.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        print("Please check your database configuration and models.")
        # Decide if you want to exit or try to run the app anyway
        # sys.exit(1)

    print("Starting Flask development server...")
    # Debug mode should ideally be controlled by an environment variable for production
    # For example: app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
