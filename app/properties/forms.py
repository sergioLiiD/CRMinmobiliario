from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, MultipleFileField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_wtf.file import FileAllowed, FileField
from .models import Fraccionamiento, Prototipo

class PrototipoForm(FlaskForm):
    nombre_prototipo = StringField('Nombre de Prototipo', validators=[DataRequired(message='El nombre es requerido')])
    superficie_terreno = FloatField('Superficie de Terreno', validators=[
        DataRequired(message='La superficie de terreno es requerida'),
        NumberRange(min=0, message='La superficie debe ser mayor a 0')
    ])
    superficie_construccion = FloatField('Superficie de Construcción', validators=[
        DataRequired(message='La superficie de construcción es requerida'),
        NumberRange(min=0, message='La superficie debe ser mayor a 0')
    ])
    niveles = IntegerField('Niveles', validators=[
        DataRequired(message='El número de niveles es requerido'),
        NumberRange(min=1, message='Debe tener al menos 1 nivel')
    ])
    recamaras = IntegerField('Número de Recámaras', validators=[
        DataRequired(message='El número de recámaras es requerido'),
        NumberRange(min=1, message='Debe tener al menos 1 recámara')
    ])
    banos = FloatField('Baños', validators=[
        DataRequired(message='El número de baños es requerido'),
        NumberRange(min=0.5, message='Debe tener al menos 0.5 baños')
    ])
    observaciones = TextAreaField('Observaciones')
    precio = FloatField('Precio', validators=[
        DataRequired(message='El precio es requerido'),
        NumberRange(min=0, message='El precio debe ser mayor a 0')
    ])
    imagenes = MultipleFileField('Imágenes')

    def validate_on_submit(self):
        print("Starting form validation")
        if not super().validate_on_submit():
            print("Form validation failed")
            print("Form errors:", self.errors)
            return False
            
        print("Form validation successful")
        return True

class FraccionamientoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message='El nombre es requerido')])
    ubicacion = StringField('Ubicación')
    logo = FileField('Logo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imágenes')
    ])
    sembrado = FileField('Sembrado (Plano General)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Solo se permiten imágenes y PDF')
    ])
    submit = SubmitField('Guardar')

class PaqueteForm(FlaskForm):
    nombre = StringField('Nombre del Paquete', validators=[DataRequired(message='El nombre es requerido')])
    submit = SubmitField('Guardar Paquete')

class LoteForm(FlaskForm):
    prototipo_id = SelectField('Prototipo', coerce=int, validators=[DataRequired()])
    calle = StringField('Calle', validators=[DataRequired()])
    numero_exterior = IntegerField('Número Exterior', validators=[DataRequired()])
    numero_interior = StringField('Número Interior')
    manzana = StringField('Manzana', validators=[DataRequired()])
    lote = StringField('Lote', validators=[DataRequired()])
    cuv = StringField('CUV')
    terreno = FloatField('Terreno')
    tipo_de_lote = SelectField('Tipo de Lote', 
        choices=[
            ('Regular', 'Regular'),
            ('Irregular', 'Irregular'),
            ('En Esquina', 'En Esquina'),
            ('En Esquina con Area Verde', 'En Esquina con Area Verde')
        ],
        validators=[DataRequired()]
    )
    estado_del_inmueble = SelectField('Estado del Inmueble',
        choices=[
            ('', 'Todos'),
            ('Libre', 'Libre'),
            ('Apartado', 'Apartado'),
            ('Titulado', 'Titulado')
        ],
        default='Libre',
        validators=[DataRequired()]
    )
    precio = FloatField('Precio', validators=[DataRequired()])
    
    orientacion_1 = SelectField('Orientación 1',
        choices=[
            ('', 'Seleccionar...'),
            ('Norte', 'Norte'),
            ('Sur', 'Sur'),
            ('Este', 'Este'),
            ('Oeste', 'Oeste'),
            ('Noreste', 'Noreste'),
            ('Noroeste', 'Noroeste'),
            ('Sureste', 'Sureste'),
            ('Suroeste', 'Suroeste')
        ],
        validators=[]
    )
    medidas_orientacion_1 = StringField('Medidas Orientación 1')
    colindancia_1 = StringField('Colindancia 1')
    
    orientacion_2 = SelectField('Orientación 2',
        choices=[
            ('', 'Seleccionar...'),
            ('Norte', 'Norte'),
            ('Sur', 'Sur'),
            ('Este', 'Este'),
            ('Oeste', 'Oeste'),
            ('Noreste', 'Noreste'),
            ('Noroeste', 'Noroeste'),
            ('Sureste', 'Sureste'),
            ('Suroeste', 'Suroeste')
        ],
        validators=[]
    )
    medidas_orientacion_2 = StringField('Medidas Orientación 2')
    colindancia_2 = StringField('Colindancia 2')
    
    orientacion_3 = SelectField('Orientación 3',
        choices=[
            ('', 'Seleccionar...'),
            ('Norte', 'Norte'),
            ('Sur', 'Sur'),
            ('Este', 'Este'),
            ('Oeste', 'Oeste'),
            ('Noreste', 'Noreste'),
            ('Noroeste', 'Noroeste'),
            ('Sureste', 'Sureste'),
            ('Suroeste', 'Suroeste')
        ],
        validators=[]
    )
    medidas_orientacion_3 = StringField('Medidas Orientación 3')
    colindancia_3 = StringField('Colindancia 3')
    
    orientacion_4 = SelectField('Orientación 4',
        choices=[
            ('', 'Seleccionar...'),
            ('Norte', 'Norte'),
            ('Sur', 'Sur'),
            ('Este', 'Este'),
            ('Oeste', 'Oeste'),
            ('Noreste', 'Noreste'),
            ('Noroeste', 'Noroeste'),
            ('Sureste', 'Sureste'),
            ('Suroeste', 'Suroeste')
        ],
        validators=[]
    )
    medidas_orientacion_4 = StringField('Medidas Orientación 4')
    colindancia_4 = StringField('Colindancia 4')
    
    submit = SubmitField('Guardar Lote')

    def __init__(self, *args, **kwargs):
        super(LoteForm, self).__init__(*args, **kwargs)
        self.prototipo_id.choices = [
            (p.id, p.nombre_prototipo) for p in Prototipo.query.order_by('nombre_prototipo').all()
        ]

class LoteFilterForm(FlaskForm):
    fraccionamiento = SelectField('Fraccionamiento', coerce=int, validators=[DataRequired()])
    paquete = SelectField('Paquete', coerce=int, validators=[Optional()])
    estado = SelectField('Estado', choices=[
        ('', 'Todos'),
        ('Libre', 'Libre'),
        ('Apartado', 'Apartado'),
        ('Titulado', 'Titulado')
    ], validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(LoteFilterForm, self).__init__(*args, **kwargs)
        self.fraccionamiento.choices = [(f.id, f.nombre) for f in Fraccionamiento.query.order_by('nombre').all()]
        self.paquete.choices = [(0, 'Todos los paquetes')]  # Default choice

class LoteBulkUploadForm(FlaskForm):
    file = FileField('Archivo CSV', validators=[
        DataRequired(),
        FileAllowed(['csv'], 'Solo se permiten archivos CSV')
    ])
    submit = SubmitField('Subir Lotes')
