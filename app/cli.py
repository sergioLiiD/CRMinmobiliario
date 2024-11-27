import click
from flask.cli import with_appcontext
from .auth.models import User, UserRole
from .database import db

@click.command('create-admin')
@click.option('--username', prompt=True, help='Username for the admin user')
@click.option('--email', prompt=True, help='Email for the admin user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the admin user')
@click.option('--nombre', prompt=True, help='First name for the admin user')
@click.option('--apellido-paterno', prompt=True, help='Last name (paterno) for the admin user')
@click.option('--apellido-materno', prompt=True, help='Last name (materno) for the admin user')
@with_appcontext
def create_admin_command(username, email, password, nombre, apellido_paterno, apellido_materno):
    """Create a new admin user."""
    user = User.query.filter_by(username=username).first()
    if user is not None:
        click.echo('Error: Username already exists.')
        return

    user = User.query.filter_by(email=email).first()
    if user is not None:
        click.echo('Error: Email already exists.')
        return

    user = User(
        username=username,
        email=email,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        role=UserRole.ADMIN.value
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    click.echo('Admin user created successfully.')
