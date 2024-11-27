from app import create_app, db
from app.clients.models import Client
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        # Create a test client
        test_client = Client(
            nombre='Test',
            apellido_paterno='User',
            apellido_materno='Test',
            celular='1234567890',
            assigned_user_id=1,  # Assuming user ID 1 exists
            estatus='activo',
            fecha_registro=datetime.utcnow()
        )
        
        # Print client details before saving
        print("Client details before save:")
        print(f"nombre: {test_client.nombre}")
        print(f"apellido_paterno: {test_client.apellido_paterno}")
        print(f"apellido_materno: {test_client.apellido_materno}")
        print(f"celular: {test_client.celular}")
        print(f"assigned_user_id: {test_client.assigned_user_id}")
        print(f"estatus: {test_client.estatus}")
        
        # Try to add and commit
        db.session.add(test_client)
        db.session.commit()
        
        print(f"Success! Client created with ID: {test_client.id}")
        
    except Exception as e:
        print(f"Error creating client: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
