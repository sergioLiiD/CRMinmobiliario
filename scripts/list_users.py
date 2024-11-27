import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.auth.models import User
from app.core.database import db

app = create_app()
with app.app_context():
    users = User.query.all()
    print("\nUsuarios Registrados:")
    print("-" * 80)
    print(f"{'ID':<5} {'Usuario':<15} {'Nombre':<15} {'Apellido P':<15} {'Apellido M':<15} {'Email':<25}")
    print("-" * 80)
    for user in users:
        print(f"{user.id:<5} {user.username:<15} {user.nombre:<15} {user.apellido_paterno:<15} {user.apellido_materno:<15} {user.email:<25}")
    print("-" * 80)
    print(f"Total de usuarios: {len(users)}\n")
