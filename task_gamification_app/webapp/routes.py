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
    get_leaderboard_users,
    UsernameExistsError,
    UserCreationError
)
from task_gamification_app.app.db import SessionLocal # For getting a db session

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

# Placeholder for other routes like task management, leaderboard etc.
# @app.route('/tasks')
# def view_tasks():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     # ... fetch and display tasks ...
#     return "Tasks Page (To be implemented)"

@app.route('/leaderboard')
def leaderboard():
    db_session = None
    try:
        db_session = SessionLocal()
        users = get_leaderboard_users(db_session=db_session, limit=20)
        return render_template('leaderboard.html', title='Leaderboard', users=users)
    except Exception as e:
        flash(f'Could not load leaderboard: {e}', 'danger')
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