from app.database import db
from datetime import datetime

# Define choices for client status
ESTATUS_CHOICES = [
    ('nuevo', 'Nuevo'),
    ('activo', 'Activo'),
    ('en_seguimiento', 'En Seguimiento'),
    ('inactivo', 'Inactivo')
]

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos Personales
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    sexo = db.Column(db.String(20), nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    regimen_matrimonial = db.Column(db.String(50), nullable=True)
    nacionalidad = db.Column(db.String(50), nullable=True)
    rfc = db.Column(db.String(13), nullable=True)
    curp = db.Column(db.String(18), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    celular = db.Column(db.String(20), nullable=False)
    tipo_de_credito = db.Column(db.String(50), nullable=True)
    banco = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    colonia = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(64), nullable=True)
    estado = db.Column(db.String(64), nullable=True)
    codigo_postal = db.Column(db.String(10), nullable=True)
    como_se_entero = db.Column(db.String(50), nullable=True)

    # Información Laboral
    nombre_empresa = db.Column(db.String(100), nullable=True)
    puesto = db.Column(db.String(100), nullable=True)
    antiguedad = db.Column(db.String(50), nullable=True)
    direccion_empresa = db.Column(db.String(200), nullable=True)
    email_empresa = db.Column(db.String(100), nullable=True)
    rfc_empresa = db.Column(db.String(13), nullable=True)
    nrp = db.Column(db.String(20), nullable=True)  # Número de Registro Patronal
    telefono = db.Column(db.String(10), nullable=True)  # Exactly 10 digits
    extension = db.Column(db.String(10), nullable=True)
    url = db.Column(db.String(200), nullable=True)
    horario = db.Column(db.String(100), nullable=True)
    ingreso_mensual = db.Column(db.Numeric(10, 2), nullable=True)
    ingresos_adicionales = db.Column(db.String(200), nullable=True)
    empresa_colonia = db.Column(db.String(100), nullable=True)
    empresa_estado = db.Column(db.String(50), nullable=True)
    empresa_codigo_postal = db.Column(db.String(10), nullable=True)

    # Referencias
    ref1_nombre = db.Column(db.String(200), nullable=True)
    apellido_paterno_referencia_1 = db.Column(db.String(100), nullable=True)
    apellido_materno_referencia_1 = db.Column(db.String(100), nullable=True)
    telefono_celular_referencia_1 = db.Column(db.String(10), nullable=True)
    direccion_referencia_1 = db.Column(db.String(200), nullable=True)
    estado_referencia_1 = db.Column(db.String(64), nullable=True)
    colonia_referencia_1 = db.Column(db.String(100), nullable=True)
    entidad_referencia_1 = db.Column(db.String(64), nullable=True)
    municipio_referencia_1 = db.Column(db.String(64), nullable=True)
    codigo_postal_referencia_1 = db.Column(db.String(10), nullable=True)

    ref2_nombre = db.Column(db.String(200), nullable=True)
    apellido_paterno_referencia_2 = db.Column(db.String(100), nullable=True)
    apellido_materno_referencia_2 = db.Column(db.String(100), nullable=True)
    telefono_celular_referencia_2 = db.Column(db.String(10), nullable=True)
    direccion_referencia_2 = db.Column(db.String(200), nullable=True)
    estado_referencia_2 = db.Column(db.String(64), nullable=True)
    colonia_referencia_2 = db.Column(db.String(100), nullable=True)
    entidad_referencia_2 = db.Column(db.String(64), nullable=True)
    municipio_referencia_2 = db.Column(db.String(64), nullable=True)
    codigo_postal_referencia_2 = db.Column(db.String(10), nullable=True)

    # Información del Cónyuge (opcional)
    conyuge_nombre = db.Column(db.String(64), nullable=True)
    conyuge_apellido_paterno = db.Column(db.String(64), nullable=True)
    conyuge_apellido_materno = db.Column(db.String(64), nullable=True)
    conyuge_fecha_nacimiento = db.Column(db.Date, nullable=True)
    conyuge_rfc = db.Column(db.String(13), nullable=True)
    conyuge_curp = db.Column(db.String(18), nullable=True)

    # Metadata
    fecha_registro = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    estatus = db.Column(db.String(50), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    notas_seguimiento = db.Column(db.Text, nullable=True, server_default='')
    fecha_ultimo_contacto = db.Column(db.Date, nullable=True)
    fecha_siguiente_contacto = db.Column(db.Date, nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Información Laboral del Cónyuge
    conyuge_nombre_empresa = db.Column(db.String(100), nullable=True)
    conyuge_puesto = db.Column(db.String(100), nullable=True)
    conyuge_antiguedad = db.Column(db.Integer, nullable=True)  # en meses
    conyuge_ingreso_mensual = db.Column(db.Float, nullable=True)
    conyuge_email = db.Column(db.String(120), nullable=True)
    conyuge_telefono = db.Column(db.String(20), nullable=True)
    conyuge_celular = db.Column(db.String(20), nullable=True)

    documents = db.relationship('Document', backref='client', lazy=True)

    @property
    def nombre_completo(self):
        """Returns the full name of the client."""
        return f"{self.apellido_paterno}, {self.apellido_materno} {self.nombre}"

    @property
    def conyuge_nombre_completo(self):
        if self.conyuge_nombre:
            return f"{self.conyuge_nombre} {self.conyuge_apellido_paterno} {self.conyuge_apellido_materno}"
        return None

    def __repr__(self):
        return f'<Client {self.nombre} {self.apellido_paterno} {self.apellido_materno}>'
