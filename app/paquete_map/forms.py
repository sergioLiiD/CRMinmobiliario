from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FloatField, StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError
from app.properties.models import Fraccionamiento, Paquete, Lote
from .models import LotStatus
from app.database import db

class MapImageUploadForm(FlaskForm):
    """
    Form for uploading map images
    """
    map_file = FileField('Map Image', validators=[
        FileAllowed(['jpg', 'png', 'pdf'], 'Images and PDFs only!')
    ])
    is_active = SelectField('Set as Active Map', 
        choices=[('true', 'Yes'), ('false', 'No')], 
        validators=[DataRequired()]
    )

class MapLocationForm(FlaskForm):
    """
    Form for creating/updating map locations
    """
    fraccionamiento = SelectField('Fraccionamiento', 
        choices=[], 
        coerce=lambda x: int(x) if x is not None else None,
        validators=[DataRequired()]
    )
    
    paquete = SelectField('Paquete', 
        choices=[], 
        coerce=lambda x: int(x) if x is not None else None,
        validators=[DataRequired()]
    )
    
    lot_id = SelectField('Lot', 
        choices=[], 
        coerce=lambda x: int(x) if x is not None else None,
        validators=[DataRequired()]
    )
    
    map_image_id = IntegerField('Map Image ID', validators=[DataRequired()])
    
    x_coordinate = FloatField('X Coordinate', validators=[DataRequired()])
    y_coordinate = FloatField('Y Coordinate', validators=[DataRequired()])
    
    status = SelectField('Status', 
        choices=[
            ('Libre', 'Libre'), 
            ('Apartado', 'Apartado'), 
            ('Titulado', 'Titulado')
        ],
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Save Lot Location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate Fraccionamiento choices with a default option
        fraccionamientos = Fraccionamiento.query.order_by(Fraccionamiento.nombre).all()
        self.fraccionamiento.choices = [(None, 'Select Fraccionamiento')] + [
            (f.id, f.nombre) for f in fraccionamientos
        ]
        
        # Populate Paquete choices with a default option
        self.paquete.choices = [(None, 'Select Paquete')]
        
        # Populate Lot choices with a default option
        self.lot_id.choices = [(None, 'Select Lot')]

    def validate_status(self, field):
        """
        Custom validation to normalize status
        """
        # Define valid statuses
        valid_statuses = ['Libre', 'Apartado', 'Titulado']
        
        # Normalize status to title case and strip whitespace
        normalized_status = field.data.strip().capitalize()
        
        # Validate and normalize status
        if normalized_status not in valid_statuses:
            # If not a valid status, default to 'Libre'
            normalized_status = 'Libre'
        
        # Update the field data with the normalized status
        field.data = normalized_status
