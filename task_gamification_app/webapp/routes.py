from flask import render_template, url_for, flash, redirect, request, session
from . import app  # Import the app instance from webapp/__init__.py
from .forms import RegistrationForm, LoginForm

# Adjust path to import service functions and custom exceptions
# This assumes webapp is a sibling to app, or sys.path is managed correctly
import sys
import os
# Add project root to sys.path to allow absolute imports like from app.services
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from task_gamification_app.app.services import (
    create_user as create_user_service,
    verify_user_login as verify_user_login_service,
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

# @app.route('/leaderboard')
# def web_leaderboard():
#     # ... fetch and display leaderboard ...
#     return "Leaderboard Page (To be implemented)"
