from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, UserEditForm
from app.auth.models import User, UserRole
from app.core.database import db
from functools import wraps
from datetime import datetime

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role(UserRole.ADMIN):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'error')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nombre=form.nombre.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicidades, su registro ha sido exitoso!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registro', form=form)

@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/admin_users.html', 
                         title='Administrar Usuarios',
                         users=users)

@bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_new_user():
    form = UserEditForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nombre=form.nombre.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            role=form.role.data,
            created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        # Handle team leader assignment
        if form.team_leader.data != 0:
            team_leader = User.query.get(form.team_leader.data)
            if team_leader and team_leader.has_role(UserRole.LIDER):
                user.team_leader = team_leader
        
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('auth.admin_users'))
    return render_template('auth/user_form.html', 
                         title='Nuevo Usuario',
                         form=form)

@bp.route('/admin/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(original_username=user.username)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.nombre = form.nombre.data
        user.apellido_paterno = form.apellido_paterno.data
        user.apellido_materno = form.apellido_materno.data
        user.role = form.role.data
        
        if form.password.data:
            user.set_password(form.password.data)
            
        # Handle team leader assignment
        if form.team_leader.data != 0:
            team_leader = User.query.get(form.team_leader.data)
            if team_leader and team_leader.has_role(UserRole.LIDER):
                user.team_leader = team_leader
        else:
            user.team_leader = None
            
        db.session.commit()
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('auth.admin_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.nombre.data = user.nombre
        form.apellido_paterno.data = user.apellido_paterno
        form.apellido_materno.data = user.apellido_materno
        form.role.data = user.role
        form.team_leader.data = user.team_leader.id if user.team_leader else 0
    
    return render_template('auth/user_form.html',
                         title='Editar Usuario',
                         form=form)

@bp.route('/admin/user/<int:id>/delete')
@login_required
@admin_required
def admin_delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'error')
        return redirect(url_for('auth.admin_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('auth.admin_users'))
