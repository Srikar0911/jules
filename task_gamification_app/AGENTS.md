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

## Future Development (Web Interface)

*   If a web interface is developed later (e.g., using Flask or Django), ensure a clear separation of concerns between the core logic and the web presentation layer.
*   The existing core logic (`models.py`, `db.py`) should be reusable.

## Gamification Logic

*   Points awarded for tasks should be configurable or based on task difficulty/priority if implemented.
*   Leaderboard updates should be efficient.

Remember to check this file for guidance when modifying or adding features to the project.
