from flask import render_template, url_for, flash, redirect, request, session
from . import app  # Import the app instance from webapp/__init__.py
from .forms import RegistrationForm, LoginForm

# Adjust path to import service functions and custom exceptions
# This assumes webapp is a sibling to app, or sys.path is managed correctly
# NOTE: The 'sys.path' modification has been removed.
# The web application should be run as a module from the project root, e.g.,
# python -m task_gamification_app.run_web
from task_gamification_app.app.services import (
    create_user as create_user_service,
    verify_user_login as verify_user_login_service,
    # get_leaderboard_users, # Old one, replaced by paginated version
    get_leaderboard_users_paginated, # New paginated version
    UsernameExistsError,
    UserCreationError,
    # Task related services and exceptions
    create_task_for_user as create_task_service,
    get_tasks_for_user as get_tasks_service,
    complete_task as complete_task_service,
    update_task_details as update_task_service,
    delete_task_for_user as delete_task_service,
    TaskNotFoundError,
    ServiceError as TaskServiceError # Alias to avoid confusion if other ServiceErrors exist
)
from task_gamification_app.app.models import TaskStatus # For filtering
from task_gamification_app.app.db import SessionLocal # For getting a db session
from .forms import CreateTaskForm, UpdateTaskForm, FilterTasksForm # Task forms
from functools import wraps # For login_required decorator

# Decorator for routes that require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
def index():
    username = session.get('username')
    return render_template('index.html', title='Home', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'): # If already logged in, redirect to home
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        db_session = None
        try:
            db_session = SessionLocal()
            new_user = create_user_service(
                db_session=db_session,
                username=form.username.data,
                password=form.password.data
            )
            flash(f'Account created for {form.username.data}! You can now log in.', 'success')
            return redirect(url_for('login'))
        except UsernameExistsError:
            flash('That username is already taken. Please choose a different one.', 'danger')
        except UserCreationError as e:
            flash(f'Account creation failed: {e}', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred: {e}', 'danger')
        finally:
            if db_session:
                db_session.close()
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'): # If already logged in, redirect to home
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        db_session = None
        try:
            db_session = SessionLocal()
            user = verify_user_login_service(
                db_session=db_session,
                username=form.username.data,
                password=form.password.data
            )
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('You have been logged in!', 'success')
                # Redirect to the page the user was trying to access, or home
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred during login: {e}', 'danger')
        finally:
            if db_session:
                db_session.close()
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- My Tasks Page ---
@app.route('/my_tasks', methods=['GET', 'POST'])
@login_required
def my_tasks():
    user_id = session['user_id']
    db_session = SessionLocal()

    create_form = CreateTaskForm()
    filter_form = FilterTasksForm(request.args) # Populate with query params for GET requests

    tasks = []
    current_filter_status_str = request.args.get('status', '').upper()
    current_filter_status = None
    if current_filter_status_str == 'PENDING':
        current_filter_status = TaskStatus.PENDING
    elif current_filter_status_str == 'COMPLETED':
        current_filter_status = TaskStatus.COMPLETED

    # Handle task creation
    if create_form.validate_on_submit() and 'create_submit' in request.form:
        try:
            create_task_service(
                db_session=db_session,
                user_id=user_id,
                description=create_form.description.data,
                due_date=create_form.due_date.data
            )
            flash('Task created successfully!', 'success')
            return redirect(url_for('my_tasks', status=current_filter_status_str)) # Preserve filter
        except TaskServiceError as e:
            flash(f'Error creating task: {e}', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred: {e}', 'danger')

    try:
        tasks = get_tasks_service(db_session=db_session, user_id=user_id, status=current_filter_status, sort_by="due_date")
    except Exception as e:
        flash(f'Error fetching tasks: {e}', 'danger')

    db_session.close() # Close session after use for GET or after POST handling if not redirected

    # For rendering, ensure the filter form reflects the current filter
    if not filter_form.status.data : filter_form.status.data = current_filter_status_str if current_filter_status_str else ""


    return render_template('my_tasks.html',
                           title='My Tasks',
                           create_form=create_form,
                           filter_form=filter_form,
                           tasks=tasks,
                           TaskStatus=TaskStatus, # Pass TaskStatus enum to template for comparisons
                           current_filter_status_str=current_filter_status_str)

@app.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    db_session = SessionLocal()
    user_id = session['user_id']
    try:
        # Fetch the task first to ensure it belongs to the user and exists for GET request
        task = db_session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            flash('Task not found or you do not have permission to edit it.', 'danger')
            db_session.close()
            return redirect(url_for('my_tasks'))

        form = UpdateTaskForm(obj=task) # Pre-populate form with task data for GET

        if form.validate_on_submit():
            try:
                updated_task = update_task_service(
                    db_session=db_session,
                    task_id=task_id,
                    user_id=user_id,
                    description=form.description.data,
                    due_date=form.due_date.data,
                    set_due_date_none=(form.due_date.data is None) # Explicitly set due_date to None if form field is empty
                )
                flash('Task updated successfully!', 'success')
                return redirect(url_for('my_tasks'))
            except TaskNotFoundError:
                flash('Task not found or you do not have permission to edit it.', 'danger')
            except TaskServiceError as e:
                flash(f'Error updating task: {e}', 'danger')
            except Exception as e:
                flash(f'An unexpected error occurred: {e}', 'danger')

        db_session.close() # Close session if not submitted or if error during submit
        return render_template('update_task.html', title='Update Task', form=form, task_id=task_id)

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        if db_session: db_session.close()
        return redirect(url_for('my_tasks'))


@app.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task_route(task_id):
    db_session = SessionLocal()
    user_id = session['user_id']
    try:
        complete_task_service(db_session=db_session, task_id=task_id, user_id=user_id)
        flash('Task marked as complete!', 'success')
    except TaskNotFoundError:
        flash('Task not found or you do not have permission to complete it.', 'danger')
    except TaskServiceError as e:
        flash(f'Error completing task: {e}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {e}', 'danger')
    finally:
        if db_session: db_session.close()
    return redirect(request.referrer or url_for('my_tasks'))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task_route(task_id):
    db_session = SessionLocal()
    user_id = session['user_id']
    try:
        delete_task_service(db_session=db_session, task_id=task_id, user_id=user_id)
        flash('Task deleted successfully!', 'success')
    except TaskNotFoundError:
        flash('Task not found or you do not have permission to delete it.', 'danger')
    except TaskServiceError as e:
        flash(f'Error deleting task: {e}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {e}', 'danger')
    finally:
        if db_session: db_session.close()
    return redirect(request.referrer or url_for('my_tasks'))


import math # For math.ceil for total_pages calculation

@app.route('/leaderboard')
@login_required
def leaderboard():
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Users per page, as requested
    db_session = SessionLocal()
    try:
        leaderboard_entries, total_users_count = get_leaderboard_users_paginated(
            db_session=db_session, page=page, per_page=per_page
        )

        total_pages = math.ceil(total_users_count / per_page)

        return render_template('leaderboard.html',
                               title='Leaderboard',
                               users=leaderboard_entries,
                               current_page=page,
                               total_pages=total_pages,
                               per_page=per_page) # Pass per_page for rank calculation if needed from base 0
    except Exception as e:
        flash(f'Could not load leaderboard: {e}', 'danger')
        # Render the leaderboard page with an error message or redirect
        # For now, redirecting to index on major error
        return redirect(url_for('index'))
    finally:
        if db_session:
            db_session.close()

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')