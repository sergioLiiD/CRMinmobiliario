from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, IntegerField, DecimalField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, Regexp
from datetime import date
import re
from app.clients.models import ESTATUS_CHOICES
from app.auth.models import User, UserRole
from flask_login import current_user

def validate_phone(form, field):
    if not re.match(r'^\d{10}$', field.data):
        raise ValidationError('El teléfono debe contener exactamente 10 dígitos')

class ClientForm(FlaskForm):
    # Datos Personales
    assigned_user_id = SelectField('Asignado a', coerce=int, validators=[DataRequired(message='El usuario asignado es requerido')])
    nombre = StringField('Nombre', validators=[DataRequired(message='El nombre es requerido'), Length(max=100)])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired(message='El apellido paterno es requerido'), Length(max=100)])
    apellido_materno = StringField('Apellido Materno', validators=[DataRequired(message='El apellido materno es requerido'), Length(max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[Optional()])
    nacionalidad = SelectField('Nacionalidad',
                             choices=[('', 'Seleccionar...'),
                                    ('mexicana', 'Mexicana'),
                                    ('extranjera', 'Extranjera')],
                             validators=[Optional()])
    sexo = SelectField('Sexo', choices=[('', 'Seleccionar...'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[Optional()])
    estado_civil = SelectField('Estado Civil',
                             choices=[('', 'Seleccionar...'), 
                                    ('soltero', 'Soltero'), 
                                    ('casado', 'Casado'),
                                    ('divorciado', 'Divorciado'),
                                    ('viudo', 'Viudo'),
                                    ('union_libre', 'Unión Libre')],
                             validators=[Optional()])
    regimen_matrimonial = SelectField('Régimen Matrimonial',
                                    choices=[('', 'Seleccionar...'),
                                           ('bienes_separados', 'Bienes Separados'),
                                           ('sociedad_conyugal', 'Sociedad Conyugal')],
                                    validators=[Optional()])
    rfc = StringField('RFC', validators=[Optional(), Length(min=12, max=13, message='El RFC debe tener entre 12 y 13 caracteres')])
    curp = StringField('CURP', validators=[Optional(), Length(min=18, max=18, message='El CURP debe tener 18 caracteres')])
    email = StringField('Email', validators=[Optional(), Email(message='Por favor ingrese un email válido'), Length(max=120)])
    telefono = StringField('Teléfono Fijo', validators=[Optional(), validate_phone])
    celular = StringField('Celular', validators=[
        DataRequired(message='El celular es requerido'),
        Regexp(r'^\d{10}$', message='El celular debe tener exactamente 10 dígitos')
    ])
    tipo_de_credito = SelectField('Tipo de Crédito',
                               choices=[('', 'Seleccionar...'),
                                      ('infonavit', 'Infonavit'),
                                      ('fovissste', 'Fovissste'),
                                      ('bancario', 'Bancario'),
                                      ('contado', 'Contado')],
                               validators=[Optional()])
    banco = StringField('Banco', validators=[Optional()])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    colonia = StringField('Colonia', validators=[Optional(), Length(max=100)])
    ciudad = StringField('Ciudad', validators=[Optional(), Length(max=64)])
    estado = StringField('Estado', validators=[Optional(), Length(max=64)])
    codigo_postal = StringField('Código Postal', validators=[Optional(), Length(max=10)])
    como_se_entero = SelectField('¿Cómo se enteró de nosotros?',
                                choices=[
                                    ('', 'Seleccione...'),
                                    ('Pase', 'Pase'),
                                    ('Flyer', 'Flyer'),
                                    ('Anuncio en Revista', 'Anuncio en Revista'),
                                    ('Anuncio en Internet', 'Anuncio en Internet'),
                                    ('Youtube', 'Youtube'),
                                    ('TikTok', 'TikTok'),
                                    ('Google', 'Google'),
                                    ('Facebook', 'Facebook'),
                                    ('Instagram', 'Instagram'),
                                    ('Facebook Ads', 'Facebook Ads'),
                                    ('Instagram Ads', 'Instagram Ads'),
                                    ('Internet', 'Internet'),
                                    ('Referencia', 'Referencia'),
                                    ('Otros', 'Otros')
                                ],
                                validators=[Optional()])
    estatus = SelectField('Estatus', 
                         choices=ESTATUS_CHOICES,
                         default='activo',
                         validators=[DataRequired()])

    # Información Laboral
    nombre_empresa = StringField('Nombre de la Empresa', validators=[Optional(), Length(max=100)])
    puesto = StringField('Puesto', validators=[Optional(), Length(max=100)])
    antiguedad = StringField('Antigüedad', validators=[Optional(), Length(max=50)])
    direccion_empresa = StringField('Dirección de la Empresa', validators=[Optional(), Length(max=200)])
    email_empresa = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    rfc_empresa = StringField('RFC', validators=[Optional(), Length(max=13)])
    nrp = StringField('Número de Registro Patronal', validators=[Optional(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[Optional(), validate_phone])
    extension = StringField('Extensión', validators=[Optional(), Length(max=10)])
    url = StringField('URL', validators=[Optional(), Length(max=200)])
    horario = StringField('Horario', validators=[Optional(), Length(max=100)])
    ingreso_mensual = DecimalField('Ingreso Mensual', validators=[Optional()])
    ingresos_adicionales = StringField('Ingresos Adicionales', validators=[Optional(), Length(max=200)])
    empresa_colonia = StringField('Colonia', validators=[Optional(), Length(max=100)])
    empresa_estado = StringField('Estado', validators=[Optional(), Length(max=50)])
    empresa_codigo_postal = StringField('Código Postal', validators=[Optional(), Length(max=10)])

    # Referencias
    ref1_nombre = StringField('Nombre Referencia 1', validators=[Optional(), Length(max=200)])
    apellido_paterno_referencia_1 = StringField('Apellido Paterno Referencia 1', validators=[Optional(), Length(max=100)])
    apellido_materno_referencia_1 = StringField('Apellido Materno Referencia 1', validators=[Optional(), Length(max=100)])
    telefono_celular_referencia_1 = StringField('Teléfono Celular Referencia 1', validators=[Optional(), validate_phone])
    direccion_referencia_1 = StringField('Dirección Referencia 1', validators=[Optional(), Length(max=200)])
    estado_referencia_1 = StringField('Estado Referencia 1', validators=[Optional(), Length(max=64)])
    colonia_referencia_1 = StringField('Colonia Referencia 1', validators=[Optional(), Length(max=100)])
    entidad_referencia_1 = StringField('Entidad Referencia 1', validators=[Optional(), Length(max=64)])
    municipio_referencia_1 = StringField('Municipio Referencia 1', validators=[Optional(), Length(max=64)])
    codigo_postal_referencia_1 = StringField('Código Postal Referencia 1', validators=[Optional(), Length(max=10)])

    ref2_nombre = StringField('Nombre Referencia 2', validators=[Optional(), Length(max=200)])
    apellido_paterno_referencia_2 = StringField('Apellido Paterno Referencia 2', validators=[Optional(), Length(max=100)])
    apellido_materno_referencia_2 = StringField('Apellido Materno Referencia 2', validators=[Optional(), Length(max=100)])
    telefono_celular_referencia_2 = StringField('Teléfono Celular Referencia 2', validators=[Optional(), validate_phone])
    direccion_referencia_2 = StringField('Dirección Referencia 2', validators=[Optional(), Length(max=200)])
    estado_referencia_2 = StringField('Estado Referencia 2', validators=[Optional(), Length(max=64)])
    colonia_referencia_2 = StringField('Colonia Referencia 2', validators=[Optional(), Length(max=100)])
    entidad_referencia_2 = StringField('Entidad Referencia 2', validators=[Optional(), Length(max=64)])
    municipio_referencia_2 = StringField('Municipio Referencia 2', validators=[Optional(), Length(max=64)])
    codigo_postal_referencia_2 = StringField('Código Postal Referencia 2', validators=[Optional(), Length(max=10)])

    # Información del Cónyuge
    conyuge_nombre = StringField('Nombre del Cónyuge', validators=[Optional(), Length(max=64)])
    conyuge_apellido_paterno = StringField('Apellido Paterno del Cónyuge', validators=[Optional(), Length(max=64)])
    conyuge_apellido_materno = StringField('Apellido Materno del Cónyuge', validators=[Optional(), Length(max=64)])
    conyuge_fecha_nacimiento = DateField('Fecha de Nacimiento del Cónyuge', format='%d-%m-%Y', validators=[Optional()])
    conyuge_rfc = StringField('RFC del Cónyuge', validators=[Optional(), Length(min=12, max=13)])
    conyuge_curp = StringField('CURP del Cónyuge', validators=[Optional(), Length(min=18, max=18)])
    conyuge_email = StringField('Email del Cónyuge', validators=[Optional(), Email(), Length(max=120)])
    conyuge_telefono = StringField('Teléfono del Cónyuge', validators=[Optional(), validate_phone])
    conyuge_celular = StringField('Celular del Cónyuge', validators=[Optional(), validate_phone])
    conyuge_nombre_empresa = StringField('Empresa del Cónyuge', validators=[Optional(), Length(max=100)])
    conyuge_puesto = StringField('Puesto del Cónyuge', validators=[Optional(), Length(max=100)])
    conyuge_antiguedad = IntegerField('Antigüedad del Cónyuge (meses)', validators=[Optional()])
    conyuge_ingreso_mensual = FloatField('Ingreso Mensual del Cónyuge', validators=[Optional()])

    # Campos de seguimiento
    tipo_propiedad = SelectField('Tipo de Propiedad',
                                choices=[('', 'Seleccione...'),
                                        ('Casa', 'Casa'),
                                        ('Departamento', 'Departamento'),
                                        ('Terreno', 'Terreno'),
                                        ('Local', 'Local Comercial'),
                                        ('Oficina', 'Oficina'),
                                        ('Bodega', 'Bodega'),
                                        ('Otro', 'Otro')],
                                validators=[Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])
    notas_seguimiento = TextAreaField('Notas de Seguimiento', validators=[Optional()])
    fecha_ultimo_contacto = DateField('Fecha de Último Contacto', format='%Y-%m-%d', validators=[Optional()])
    fecha_siguiente_contacto = DateField('Fecha de Siguiente Contacto', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        
        # Get list of available users based on current user's role
        self.assigned_user_id.choices = [(current_user.id, current_user.nombre_completo)]
        if (current_user.role == UserRole.ADMIN.value or 
            current_user.role == UserRole.GERENTE.value or 
            current_user.role == UserRole.LIDER.value):
            # Add current user as first choice
            users = current_user.get_viewable_users()
            self.assigned_user_id.choices = [(current_user.id, current_user.nombre_completo)] + [
                (user.id, user.nombre_completo) for user in users if user.id != current_user.id
            ]
        
        # Set default value to current user's ID
        if not self.assigned_user_id.data:
            self.assigned_user_id.data = current_user.id

    def validate_fecha_nacimiento(self, field):
        if field.data > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser en el futuro.')
        
    def validate_conyuge_fecha_nacimiento(self, field):
        if field.data and field.data > date.today():
            raise ValidationError('La fecha de nacimiento del cónyuge no puede ser en el futuro.')


class ClientSearchForm(FlaskForm):
    busqueda = StringField('Buscar')
    estatus = SelectField('Estatus',
                         choices=[('todos', 'Todos'),
                                ('nuevo', 'Nuevo'),
                                ('activo', 'Activo'),
                                ('en_seguimiento', 'En Seguimiento'),
                                ('inactivo', 'Inactivo')],
                         default='todos',
                         validators=[Optional()])
    submit = SubmitField('Buscar')
