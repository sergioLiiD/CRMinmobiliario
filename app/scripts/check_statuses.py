import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app import create_app
from app.database import db
from app.paquete_map.models import MapLocation, LotStatus
from app.properties.models import Lote

app = create_app()

with app.app_context():
    # Check MapLocation statuses
    print('MapLocation Statuses:')
    for location in MapLocation.query.all():
        print(f'ID: {location.id}, Status: {location.status}')
    
    print('\nLote Statuses:')
    for lote in Lote.query.all():
        print(f'ID: {lote.id}, Estado del Inmueble: {lote.estado_del_inmueble}')
