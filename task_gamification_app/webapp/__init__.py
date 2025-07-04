from flask import Flask
import os

# Initialize the Flask application
app = Flask(__name__)

# Configuration
# In a real application, this should be set via environment variables or a config file
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_default_key_for_dev')

# Import routes after app initialization to avoid circular imports
from . import routes # Assuming routes.py will be in the same directory

# You might also initialize database connections or other extensions here if needed globally
# For example, if using Flask-SQLAlchemy (though we are using standalone SQLAlchemy for now):
# from ..app.db import SessionLocal, engine # Example path
# app.db_session = SessionLocal

import datetime

@app.context_processor
def inject_now():
    return {'datetime': datetime}

print("Flask app initialized from webapp/__init__.py with datetime context processor.")
