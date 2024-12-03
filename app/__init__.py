from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from .database import db
import os

migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

def ensure_upload_dirs(app):
    """Ensure all required upload directories exist and have correct permissions"""
    upload_dirs = [
        os.path.join(app.config['UPLOAD_FOLDER'], 'prototipos'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
    ]
    
    for directory in upload_dirs:
        if not os.path.exists(directory):
            print(f"Creating upload directory: {directory}")
            os.makedirs(directory, exist_ok=True)
            # Ensure directory has correct permissions (readable and writable)
            os.chmod(directory, 0o755)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure session handling
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configure CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Don't require HTTPS for CSRF (development only)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Ensure upload directories exist
    ensure_upload_dirs(app)

    # Import all models to ensure they are registered with SQLAlchemy
    from .auth.models import User
    from .clients.models import Client, Document
    from .properties.models import Prototipo, PrototipoImagen

    # Import and register blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from .properties import bp as properties_bp
    app.register_blueprint(properties_bp, url_prefix='/properties')
    
    from .clients import bp as clients_bp
    app.register_blueprint(clients_bp, url_prefix='/clients')
    
    from .paquete_map.routes import map_bp
    app.register_blueprint(map_bp)

    # Register CLI commands
    from .cli import create_admin_command
    app.cli.add_command(create_admin_command)

    return app
