import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.paquete_map.models import MapLocation, LotStatus
from app.properties.models import Lote
from app.database import db
from app import create_app

def normalize_statuses():
    app = create_app()
    
    with app.app_context():
        # Normalize MapLocation statuses
        map_locations = MapLocation.query.all()
        print("Normalizing MapLocation statuses:")
        for location in map_locations:
            # Convert to uppercase enum
            try:
                normalized_status = location.status.name
                print(f"Location ID {location.id}: {location.status} -> {normalized_status}")
            except Exception as e:
                print(f"Error processing location {location.id}: {e}")
        
        # Normalize Lote statuses
        lotes = Lote.query.all()
        print("\nNormalizing Lote statuses:")
        for lote in lotes:
            # Convert to title case
            normalized_status = lote.estado_del_inmueble.lower().capitalize()
            print(f"Lote ID {lote.id}: {lote.estado_del_inmueble} -> {normalized_status}")
            lote.estado_del_inmueble = normalized_status
        
        # Commit changes
        try:
            db.session.commit()
            print("\nStatus normalization complete.")
        except Exception as e:
            db.session.rollback()
            print(f"\nError committing changes: {e}")

if __name__ == '__main__':
    normalize_statuses()
