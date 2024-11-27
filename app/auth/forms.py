from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.auth.models import User, UserRole

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=64)])
    apellido_materno = StringField('Apellido Materno', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor use un nombre de usuario diferente.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor use una dirección de email diferente.')

class UserEditForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=64)])
    apellido_materno = StringField('Apellido Materno', validators=[DataRequired(), Length(max=64)])
    role = SelectField('Rol', choices=[(role.value, role.value) for role in UserRole], validators=[DataRequired()])
    password = PasswordField('Nueva Contraseña (dejar en blanco para mantener la actual)')
    password2 = PasswordField('Repetir Nueva Contraseña', validators=[EqualTo('password')])
    team_leader = SelectField('Líder de Equipo', coerce=int, validators=[])
    submit = SubmitField('Guardar Cambios')

    def __init__(self, original_username=None, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        # Add empty choice for team leader
        self.team_leader.choices = [(0, 'Sin líder de equipo')] + [
            (u.id, u.nombre_completo) 
            for u in User.query.filter_by(role=UserRole.LIDER.value).all()
        ]

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Por favor use un nombre de usuario diferente.')
