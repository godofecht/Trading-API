import json
from flask import current_app
from models import db

def init_db():
    app = current_app._get_current_object()
    with app.app_context():
        db.create_all()  # Create all tables
