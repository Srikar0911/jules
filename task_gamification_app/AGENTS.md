# Agent Instructions for Task Gamification App

## General Guidelines

*   The primary goal is to build a functional and user-friendly task management application with gamification elements.
*   Prioritize clear, maintainable, and well-documented code.
*   Follow Python best practices (PEP 8).

## Database

*   Use SQLAlchemy as the ORM for interacting with an SQLite database.
*   Ensure database migrations are handled if schema changes become complex (for now, simple table creation is fine).
*   User passwords must be securely hashed using `bcrypt`.

## Command-Line Interface (CLI)

*   The CLI should be intuitive and provide clear feedback to the user.
*   Consider using a library like `click` or `argparse` for more complex CLI interactions if needed, but start simple.

## Testing

*   Write unit tests for core functionalities, especially for business logic in `models.py` and `db.py`.
*   Aim for good test coverage.
*   Tests should be placed in the `tests/` directory.

## Dependencies

*   Keep `requirements.txt` updated with all necessary dependencies.

## Web Application (Flask)

*   The web application is built using Flask.
*   Key files for the webapp are located in `task_gamification_app/webapp/`.
    *   `routes.py`: Defines the URL routes and their corresponding view functions.
    *   `forms.py`: Contains form definitions using Flask-WTF.
    *   `templates/`: Holds HTML templates, with `base.html` as the main layout.
    *   `__init__.py`: Initializes the Flask app.
*   The existing core logic (`app/models.py`, `app/services.py`, `app/db.py`) is used by the web application.
*   **Navigation**:
    *   The main navigation bar is in `webapp/templates/base.html`.
    *   It includes links to "Home", "About", and "Contact" pages. The "About" and "Contact" pages are static informational pages.
    *   User-specific links (Login, Register, Logout, My Tasks, Leaderboard) are also present and adapt based on login status.

## Gamification Logic

*   Points awarded for tasks should be configurable or based on task difficulty/priority if implemented.
*   Leaderboard updates should be efficient.

Remember to check this file for guidance when modifying or adding features to the project.
