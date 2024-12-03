from app import db
from enum import Enum as PyEnum
from sqlalchemy import Enum
from datetime import datetime

class LotStatus(PyEnum):
    LIBRE = 'LIBRE'
    APARTADO = 'APARTADO'
    TITULADO = 'TITULADO'

class MapImage(db.Model):
    """
    Represents an uploaded map image
    """
    __tablename__ = 'map_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    
    # Relationship
    map_locations = db.relationship('MapLocation', back_populates='map_image', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<MapImage {self.filename} (Active: {self.is_active})>'

class MapLocation(db.Model):
    """
    Model to store lot locations and statuses on a map
    """
    __tablename__ = 'map_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lotes.id', ondelete='CASCADE'), nullable=False)
    map_image_id = db.Column(db.Integer, db.ForeignKey('map_images.id'), nullable=False)
    
    x_coordinate = db.Column(db.Float, nullable=False)
    y_coordinate = db.Column(db.Float, nullable=False)
    
    # Change status to a string with a default
    status = db.Column(db.String(20), nullable=False, default='Libre')
    
    # Relationships
    lot = db.relationship('Lote', back_populates='map_locations')
    map_image = db.relationship('MapImage', back_populates='map_locations')
    
    def normalize_status(self):
        """
        Normalize the status to a consistent format
        """
        status_mapping = {
            'libre': 'Libre',
            'LIBRE': 'Libre',
            'Libre': 'Libre',
            'apartado': 'Apartado',
            'APARTADO': 'Apartado',
            'Apartado': 'Apartado',
            'titulado': 'Titulado',
            'TITULADO': 'Titulado',
            'Titulado': 'Titulado'
        }
        
        # Convert to string and strip whitespace
        status_str = str(self.status).strip()
        
        # Return mapped status or default to Libre
        self.status = status_mapping.get(status_str, 'Libre')
        
        return self.status
    
    def __repr__(self):
        return f'<MapLocation Lot {self.lot_id} on Map {self.map_image_id} at ({self.x_coordinate}, {self.y_coordinate}) Status: {self.status}>'
