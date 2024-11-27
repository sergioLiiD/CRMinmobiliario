from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.database import db
from app import login_manager
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    LIDER = "LIDER DE EQUIPO"
    VENDEDOR = "VENDEDOR"

# Association table for team leaders and their assigned users
team_leader_assignments = db.Table('team_leader_assignments',
    db.Column('leader_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nombre = db.Column(db.String(64), nullable=False)
    apellido_paterno = db.Column(db.String(64), nullable=False)
    apellido_materno = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False, default=UserRole.VENDEDOR.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    clients = db.relationship('Client', lazy='dynamic')
    team_members = db.relationship(
        'User',
        secondary=team_leader_assignments,
        primaryjoin=(id == team_leader_assignments.c.leader_id),
        secondaryjoin=(id == team_leader_assignments.c.user_id),
        backref=db.backref('team_leaders', lazy='dynamic'),
        lazy='dynamic'
    )

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role.value if isinstance(role, UserRole) else self.role == role

    def can_view_client(self, client):
        """Check if user has permission to view a specific client"""
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
        if self.has_role(UserRole.LIDER):
            return client.assigned_user_id in [user.id for user in self.team_members]
        return client.assigned_user_id == self.id

    def can_edit_client(self, client):
        """Check if user has permission to edit a specific client"""
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
        if self.has_role(UserRole.LIDER):
            return client.assigned_user_id in [user.id for user in self.team_members]
        return client.assigned_user_id == self.id

    def can_delete_client(self, client):
        """Check if user has permission to delete a specific client"""
        return self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE)

    def can_assign_client(self, target_user):
        """Check if user can assign a client to a specific user"""
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
        if self.has_role(UserRole.LIDER):
            return target_user.id in [user.id for user in self.team_members]
        return target_user.id == self.id

    def can_upload_documents_for_client(self, client):
        """Check if user has permission to upload documents for a specific client"""
        return self.can_edit_client(client)

    def can_delete_document(self, document):
        """Check if user has permission to delete a specific document"""
        return self.can_delete_client(document.client)

    def get_viewable_users(self):
        """
        Returns a list of users that this user can view and assign clients to,
        sorted by apellido_paterno, apellido_materno, and nombre
        """
        if self.has_role(UserRole.ADMIN.value):
            users = User.query.filter(User.is_active == True)
        elif self.has_role(UserRole.GERENTE.value):
            users = User.query.filter(User.is_active == True)
        elif self.has_role(UserRole.LIDER.value):
            users = User.query.filter(User.id.in_([user.id for user in self.team_members]))
        else:
            users = User.query.filter(User.id == self.id)
        
        return users.order_by(User.apellido_paterno, User.apellido_materno, User.nombre).all()

    def can_assign_lot(self, client, lote):
        """Check if user can assign a lot to a specific client"""
        # Admins and Gerentes can assign any lot to any client
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
            
        # Team leaders can assign lots to clients of their team members
        if self.has_role(UserRole.LIDER):
            return client.assigned_user_id in [user.id for user in self.team_members]
            
        # Regular vendors can only assign lots to their own clients
        return client.assigned_user_id == self.id

    def can_view_lot_assignment(self, asignacion):
        """Check if user can view a specific lot assignment"""
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
            
        if self.has_role(UserRole.LIDER):
            return asignacion.client.assigned_user_id in [user.id for user in self.team_members]
            
        return asignacion.client.assigned_user_id == self.id

    def can_modify_lot_assignment(self, asignacion):
        """Check if user can modify or delete a lot assignment"""
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return True
            
        if self.has_role(UserRole.LIDER):
            return asignacion.client.assigned_user_id in [user.id for user in self.team_members]
            
        return asignacion.client.assigned_user_id == self.id

    def get_assignable_clients(self):
        """Get list of clients that this user can assign lots to"""
        from app.clients.models import Client
        if self.has_role(UserRole.ADMIN) or self.has_role(UserRole.GERENTE):
            return Client.query.filter_by(estatus='activo').all()
            
        if self.has_role(UserRole.LIDER):
            team_user_ids = [user.id for user in self.team_members]
            return Client.query.filter(
                Client.assigned_user_id.in_(team_user_ids),
                Client.estatus == 'activo'
            ).all()
            
        return Client.query.filter_by(
            assigned_user_id=self.id,
            estatus='activo'
        ).all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
