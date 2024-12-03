import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from app.paquete_map.models import MapLocation

# Create the app and migration context
app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        print("Creating migration for MapLocation model...")
        # This will generate a migration script
        # You can run this with: flask db migrate -m "Add MapLocation model"
        # And then apply with: flask db upgrade
