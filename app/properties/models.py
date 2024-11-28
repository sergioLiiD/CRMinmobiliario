from app.database import db
from datetime import datetime

class PrototipoImagen(db.Model):
    __tablename__ = 'prototipo_imagenes'
    
    id = db.Column(db.Integer, primary_key=True)
    prototipo_id = db.Column(db.Integer, db.ForeignKey('prototipos.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    prototipo = db.relationship('Prototipo', back_populates='imagenes')

class Prototipo(db.Model):
    __tablename__ = 'prototipos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_prototipo = db.Column(db.String(100), nullable=False)
    superficie_terreno = db.Column(db.Float, nullable=False)
    superficie_construccion = db.Column(db.Float, nullable=False)
    niveles = db.Column(db.Integer, nullable=False)
    recamaras = db.Column(db.Integer, nullable=False)
    banos = db.Column(db.Float, nullable=False)  # Float to allow half bathrooms
    observaciones = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    imagenes = db.relationship('PrototipoImagen', back_populates='prototipo', cascade='all, delete-orphan')
    lotes = db.relationship('Lote', backref='prototipo', lazy=True)

    def __repr__(self):
        return f'<Prototipo {self.nombre_prototipo}>'

class Fraccionamiento(db.Model):
    __tablename__ = 'fraccionamiento'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=True)
    logo = db.Column(db.String(200))  # Path to logo file
    sembrado = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paquetes = db.relationship('Paquete', backref='fraccionamiento', lazy=True)

class Paquete(db.Model):
    __tablename__ = 'paquetes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fraccionamiento_id = db.Column(db.Integer, db.ForeignKey('fraccionamiento.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lotes = db.relationship('Lote', backref='paquete', lazy=True)

class Lote(db.Model):
    __tablename__ = 'lotes'
    
    id = db.Column(db.Integer, primary_key=True)
    paquete_id = db.Column(db.Integer, db.ForeignKey('paquetes.id'), nullable=False)
    prototipo_id = db.Column(db.Integer, db.ForeignKey('prototipos.id'), nullable=False)
    
    # Location details
    calle = db.Column(db.String(100), nullable=False)
    numero_exterior = db.Column(db.Integer, nullable=False)
    numero_interior = db.Column(db.String(50), nullable=True)  
    manzana = db.Column(db.String(50), nullable=False)
    lote = db.Column(db.String(50), nullable=False)
    cuv = db.Column(db.String(50), nullable=True, default=None)
    terreno = db.Column(db.Float, nullable=True, default=None)
    tipo_de_lote = db.Column(db.String(50), nullable=False)
    estado_del_inmueble = db.Column(db.String(50), nullable=False, default='Libre')
    precio = db.Column(db.Float, nullable=False)
    
    # Orientation measurements
    orientacion_1 = db.Column(db.String(50), nullable=True, default=None)
    medidas_orientacion_1 = db.Column(db.String(50), nullable=True, default=None)
    colindancia_1 = db.Column(db.String(100), nullable=True, default=None)
    orientacion_2 = db.Column(db.String(50), nullable=True, default=None)
    medidas_orientacion_2 = db.Column(db.String(50), nullable=True, default=None)
    colindancia_2 = db.Column(db.String(100), nullable=True, default=None)
    orientacion_3 = db.Column(db.String(50), nullable=True, default=None)
    medidas_orientacion_3 = db.Column(db.String(50), nullable=True, default=None)
    colindancia_3 = db.Column(db.String(100), nullable=True, default=None)
    orientacion_4 = db.Column(db.String(50), nullable=True, default=None)
    medidas_orientacion_4 = db.Column(db.String(50), nullable=True, default=None)
    colindancia_4 = db.Column(db.String(100), nullable=True, default=None)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constants for choices
    TIPOS_DE_LOTE = ['Regular', 'Irregular', 'En Esquina', 'En Esquina con Area Verde']
    ESTADOS_INMUEBLE = ['Libre', 'Apartado', 'Titulado']
    ORIENTACIONES = ['Norte', 'Sur', 'Este', 'Oeste', 'Noreste', 'Noroeste', 'Sureste', 'Suroeste']

    asignacion = db.relationship('LoteAsignacion', 
                                 uselist=False,  # One-to-one relationship
                                 back_populates='lote',
                                 cascade='all, delete-orphan')

    @property
    def is_available(self):
        """Check if the lot is available for assignment"""
        return self.estado_del_inmueble == 'Libre'

    def asignar_a_cliente(self, client, user, notas=None):
        """Assign this lot to a client"""
        if self.estado_del_inmueble != 'Libre':
            raise ValueError('Este lote no está disponible')
            
        if hasattr(self, 'asignacion') and self.asignacion is not None:
            raise ValueError('Este lote ya está asignado')
            
        # Create new assignment
        asignacion = LoteAsignacion(
            lote_id=self.id,
            client_id=client.id,
            user_id=user.id,
            notas=notas
        )
        
        # Update lot status
        self.estado_del_inmueble = 'Apartado'
        
        return asignacion

    def liberar_lote(self, user, motivo, notas=None):
        """Release this lot back to available status"""
        if not self.asignacion:
            raise ValueError('Este lote no está asignado')
            
        # Create historical record
        historial = LoteAsignacionHistorial(
            lote=self,
            client=self.asignacion.client,
            user=user,
            fecha_inicio=self.asignacion.fecha_inicio,
            fecha_fin=datetime.utcnow(),
            estado=self.asignacion.estado,
            motivo_cambio=motivo,
            notas=notas
        )
        
        # Delete current assignment
        db.session.delete(self.asignacion)
        
        # Update lot status
        self.estado_del_inmueble = 'Libre'
        
        return historial

class LoteAsignacion(db.Model):
    __tablename__ = 'lote_asignaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)  # Keep old column for compatibility
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(50), nullable=False, default='Apartado')
    notas = db.Column(db.Text, nullable=True)
    
    # Relationships
    lote = db.relationship('Lote', back_populates='asignacion')
    client = db.relationship('Client', backref='lotes_asignados')
    user = db.relationship('User', backref='asignaciones_realizadas')
    
    def __init__(self, lote_id, client_id, user_id, notas=None, fecha_inicio=None):
        self.lote_id = lote_id
        self.client_id = client_id
        self.user_id = user_id
        self.notas = notas
        self.fecha_inicio = fecha_inicio or datetime.utcnow()
        self.fecha_asignacion = self.fecha_inicio  # Keep old column in sync
        self.estado = 'Apartado'

class LoteAsignacionHistorial(db.Model):
    __tablename__ = 'lote_asignaciones_historial'
    
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who made the change
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(50), nullable=False)  # The state during this period
    motivo_cambio = db.Column(db.String(100), nullable=False)  # Reason for change
    notas = db.Column(db.Text, nullable=True)
    
    # Relationships
    lote = db.relationship('Lote', backref='historial_asignaciones')
    client = db.relationship('Client', backref='historial_lotes')
    user = db.relationship('User', backref='historial_asignaciones')

class LoteStatusChangeLog(db.Model):
    __tablename__ = 'lote_status_change_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lote = db.relationship('Lote', backref='status_changes')
    user = db.relationship('User', backref='lote_status_changes')
    
    def __repr__(self):
        return f'<LoteStatusChangeLog {self.lote_id}: {self.old_status} -> {self.new_status}>'
