from flask import render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from app.clients import bp
from app.clients.models import Client, Document, ESTATUS_CHOICES
from app.clients.forms import ClientForm, ClientSearchForm
from app import db
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.auth.models import UserRole, User
import sys
import traceback

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def index():
    search_form = ClientSearchForm()
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Client.query
    
    # Filter clients based on user role
    if not current_user.has_role(UserRole.ADMIN) and not current_user.has_role(UserRole.GERENTE):
        if current_user.has_role(UserRole.LIDER):
            # Get all clients assigned to team members
            team_member_ids = [user.id for user in current_user.team_members]
            query = query.filter(Client.assigned_user_id.in_(team_member_ids))
        else:
            # Regular vendedor can only see their own clients
            query = query.filter_by(assigned_user_id=current_user.id)
    
    # Apply filters if they exist in request args
    if request.args.get('busqueda'):
        search = f"%{request.args.get('busqueda')}%"
        query = query.filter(or_(
            Client.nombre.ilike(search),
            Client.apellido_paterno.ilike(search),
            Client.apellido_materno.ilike(search),
            Client.email.ilike(search)
        ))
    
    if request.args.get('estatus') and request.args.get('estatus') != 'todos':
        query = query.filter(Client.estatus == request.args.get('estatus'))
    
    # Paginate results
    try:
        clients = query.order_by(Client.fecha_registro.desc()).paginate(
            page=page, per_page=10, error_out=False)
    except Exception as e:
        flash('Error al cargar los clientes. Por favor, contacte al administrador.', 'error')
        clients = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('clients/index.html', 
                         clients=clients,
                         search_form=search_form)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ClientForm()
    if form.validate_on_submit():
        try:
            # Validate required fields manually
            required_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'celular', 'assigned_user_id']
            for field_name in required_fields:
                field_value = getattr(form, field_name).data
                if not field_value:
                    flash(f'El campo {field_name} es requerido.', 'error')
                    return render_template('clients/form.html', form=form, client=None, title='Nuevo Cliente')

            # Print form data for debugging
            print("\nForm data:")
            for field in form:
                if field.name != 'csrf_token':
                    print(f"{field.name}: {field.data}")
            
            # Create new client with required fields
            client = Client(
                nombre=form.nombre.data.strip(),
                apellido_paterno=form.apellido_paterno.data.strip(),
                apellido_materno=form.apellido_materno.data.strip(),
                celular=form.celular.data.strip(),
                assigned_user_id=form.assigned_user_id.data,
                estatus='activo',
                fecha_registro=datetime.utcnow()
            )
            
            # Handle optional fields
            optional_fields = {
                'email': form.email.data,
                'fecha_nacimiento': form.fecha_nacimiento.data,
                'sexo': form.sexo.data,
                'estado_civil': form.estado_civil.data,
                'nacionalidad': form.nacionalidad.data,
                'tipo_de_credito': form.tipo_de_credito.data,
                'banco': form.banco.data
            }
            
            for field_name, value in optional_fields.items():
                if value:
                    setattr(client, field_name, value.strip() if isinstance(value, str) else value)
            
            print("\nClient object before save:")
            print(f"nombre: {client.nombre}")
            print(f"apellido_paterno: {client.apellido_paterno}")
            print(f"apellido_materno: {client.apellido_materno}")
            print(f"celular: {client.celular}")
            print(f"assigned_user_id: {client.assigned_user_id}")
            print(f"estatus: {client.estatus}")
            print(f"fecha_registro: {client.fecha_registro}")
            
            # Verify user exists
            assigned_user = User.query.get(client.assigned_user_id)
            if not assigned_user:
                flash('El usuario asignado no existe.', 'error')
                return render_template('clients/form.html', form=form, client=None, title='Nuevo Cliente')
            
            try:
                db.session.add(client)
                db.session.flush()  # Try to flush changes to detect any database errors
                print("\nClient added to session successfully")
            except Exception as e:
                print(f"\nError during session.add or flush: {str(e)}")
                raise
                
            try:
                db.session.commit()
                print("\nCommit successful")
            except Exception as e:
                print(f"\nError during commit: {str(e)}")
                raise
            
            print(f"\nClient created successfully with ID: {client.id}")
            flash('Cliente creado exitosamente.', 'success')
            return redirect(url_for('clients.view', id=client.id))
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"\nIntegrityError creating client: {str(e)}")
            if "UNIQUE constraint failed: client.email" in str(e):
                flash('Error al crear el cliente. El email ya existe.', 'error')
            else:
                flash('Error de integridad en la base de datos. Por favor revise los datos.', 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"\nSQLAlchemyError creating client:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print(f"Error args: {e.args}")
            flash('Error en la base de datos. Por favor intente nuevamente.', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"\nUnexpected error creating client:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            traceback.print_exc()
            flash('Error inesperado al crear el cliente. Por favor intente nuevamente.', 'error')
    else:
        print("\nForm validation errors:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'error')
    
    return render_template('clients/form.html', form=form, client=None, title='Nuevo Cliente')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    client = Client.query.get_or_404(id)
    
    # Check if user has permission to edit this client
    if not current_user.can_edit_client(client):
        abort(403)
    
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        # Handle empty email specifically
        if not form.email.data:
            form.email.data = None
        form.populate_obj(client)
        try:
            db.session.commit()
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('clients.view', id=client.id))
        except IntegrityError:
            db.session.rollback()
            flash('Error al actualizar el cliente. El email ya existe.', 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"SQLAlchemyError updating client: {str(e)}")
            flash('Error al actualizar el cliente. Por favor intente nuevamente.', 'error')
    return render_template('clients/form.html', form=form, client=client, title='Editar Cliente')

@bp.route('/view/<int:id>')
@login_required
def view(id):
    client = Client.query.get_or_404(id)
    
    # Check if user has permission to view this client
    if not current_user.can_view_client(client):
        abort(403)
    
    if client is None:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('clients.index'))
    return render_template('clients/view.html', 
                         client=client,
                         title=f'Cliente: {client.nombre} {client.apellido_paterno} {client.apellido_materno}')

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    client = Client.query.get_or_404(id)
    
    # Check if user has permission to delete this client
    if not current_user.can_delete_client(client):
        abort(403)
    
    db.session.delete(client)
    try:
        db.session.commit()
        flash('Cliente eliminado exitosamente.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemyError deleting client: {str(e)}")
        flash('Error al eliminar el cliente. Por favor intente nuevamente.', 'error')
    return redirect(url_for('clients.index'))

@bp.route('/upload_document/<int:client_id>', methods=['POST'])
@login_required
def upload_document(client_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    document_name = request.form.get('document_name')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not document_name:
        return jsonify({'error': 'Document name is required'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Get client
            client = Client.query.get_or_404(client_id)
            
            # Check if user has permission to upload documents for this client
            if not current_user.can_upload_documents_for_client(client):
                abort(403)
            
            # Create a unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)
            
            # Create document record
            document = Document(
                name=document_name,
                filename=filename,
                client_id=client_id
            )
            db.session.add(document)
            try:
                db.session.commit()
                return jsonify({
                    'success': True,
                    'document': {
                        'id': document.id,
                        'name': document.name,
                        'filename': document.filename,
                        'upload_date': document.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"SQLAlchemyError creating document: {str(e)}")
                return jsonify({'error': 'Error al subir el documento'}), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error uploading document: {str(e)}')
            return jsonify({'error': 'Error al subir el documento'}), 500
    
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@bp.route('/document/<int:document_id>')
def get_document(document_id):
    document = Document.query.get_or_404(document_id)
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(uploads_dir, document.filename)

@bp.route('/delete_document/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Check if user has permission to delete this document
    if not current_user.can_delete_document(document):
        abort(403)
    
    # Delete file
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    file_path = os.path.join(uploads_dir, document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete record
    db.session.delete(document)
    try:
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemyError deleting document: {str(e)}")
        return jsonify({'error': 'Error al eliminar el documento'}), 500

@bp.route('/assign_user/<int:id>', methods=['POST'])
@login_required
def assign_user(id):
    client = Client.query.get_or_404(id)
    
    # Check if user has permission to assign this client
    if not current_user.can_assign_client(client.assigned_user):
        abort(403)
    
    new_user_id = request.form.get('new_user_id', type=int)
    if not new_user_id:
        flash('Usuario no válido.', 'error')
        return redirect(url_for('clients.view', id=client.id))
    
    new_user = User.query.get_or_404(new_user_id)
    if not current_user.can_assign_client(new_user):
        flash('No tienes permiso para asignar clientes a este usuario.', 'error')
        return redirect(url_for('clients.view', id=client.id))
    
    client.assigned_user_id = new_user_id
    try:
        db.session.commit()
        flash(f'Cliente asignado exitosamente a {new_user.nombre_completo}.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemyError assigning client: {str(e)}")
        flash('Error al asignar el cliente. Por favor intente nuevamente.', 'error')
    return redirect(url_for('clients.view', id=client.id))

@bp.route('/assignable')
@login_required
def get_assignable_clients():
    try:
        # Verify authentication
        if not current_user.is_authenticated:
            print("User not authenticated")
            return jsonify({'error': 'Not authenticated'}), 401

        print(f"Loading assignable clients for user {current_user.email} (Role: {current_user.role})")
        
        # Base query for active clients
        query = Client.query.filter_by(estatus='activo')
        
        # Filter clients based on user role
        if not current_user.has_role(UserRole.ADMIN) and not current_user.has_role(UserRole.GERENTE):
            print(f"User role is not admin or gerente. Role: {current_user.role}")
            if current_user.has_role(UserRole.LIDER):
                print("User is a lider")
                # Get all clients assigned to team members
                team_member_ids = [user.id for user in current_user.team_members]
                query = query.filter(Client.assigned_user_id.in_(team_member_ids))
            else:
                print("User is a regular vendedor")
                # Regular vendedor can only see their own clients
                query = query.filter_by(assigned_user_id=current_user.id)
        else:
            print("User is admin or gerente")
        
        clients = query.all()
        print(f"Found {len(clients)} assignable clients")
        
        result = [{
            'id': client.id,
            'nombre_completo': f"{client.nombre} {client.apellido_paterno} {client.apellido_materno}",
            'celular': client.celular or 'N/A'
        } for client in clients]
        
        print("Returning client list")
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json'
        return response

    except Exception as e:
        print(f"Error in get_assignable_clients: {str(e)}")
        return jsonify({'error': str(e)}), 500
