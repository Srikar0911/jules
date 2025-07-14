from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# If we need to check against existing users directly in forms (can also be done in routes)
# from ..app.models import User
# from ..app.db import SessionLocal

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    # We might add an email field later if desired
    # email = StringField('Email',
    #                     validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Example custom validator: Ensure this is adapted if User model/db session is different
    # def validate_username(self, username):
    #     db_session = SessionLocal()
    #     user = db_session.query(User).filter_by(username=username.data).first()
    #     db_session.close()
    #     if user:
    #         raise ValidationError('That username is taken. Please choose a different one.')

    # def validate_email(self, email):
    #     db_session = SessionLocal()
    #     user = db_session.query(User).filter_by(email=email.data).first() # Assuming User model has email
    #     db_session.close()
    #     if user:
    #         raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()]) # If logging in with email
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me') # Optional: for "remember me" functionality
    submit = SubmitField('Login')

# Forms for Task Management
from wtforms import TextAreaField, DateField
from wtforms.validators import Optional

class TaskForm(FlaskForm):
    description = TextAreaField('Task Description', validators=[DataRequired(), Length(min=1, max=500)])
    due_date = DateField('Due Date (YYYY-MM-DD)', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Save Task')
    delete = SubmitField('Delete Task') # For including delete on an edit form
    complete = SubmitField('Mark Complete') # For quick actions

class CreateTaskForm(TaskForm):
    # Inherits description, due_date, submit
    # Remove delete and complete as they don't make sense on a pure creation form
    submit = None # Unset the inherited submit field
    delete = None
    complete = None
    create_submit = SubmitField('Create Task')

class UpdateTaskForm(TaskForm):
    # Inherits description, due_date, submit
    # `submit` will be "Save Task"
    # `delete` can be used on this form
    pass # Uses all fields from TaskForm, submit label is fine.

from wtforms import SelectField

class FilterTasksForm(FlaskForm):
    description = StringField('Description', validators=[Optional()])
    status = SelectField('Status', choices=[('All', 'All'), ('Pending', 'Pending'), ('Completed', 'Completed')], validators=[Optional()])
    creation_date = DateField('Creation date', validators=[Optional()], format='%Y-%m-%d')
    due_date = DateField('Due date', validators=[Optional()], format='%Y-%m-%d')
    completion_date = DateField('Completion date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Filter')
