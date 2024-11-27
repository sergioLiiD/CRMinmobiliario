from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.clients import bp
from app.clients.models import Client, Document
from app.clients.forms import ClientForm, ClientSearchForm
from app.core.database import db
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
from flask import current_app, send_from_directory, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.auth.models import UserRole, User

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
            client = Client()
            # Handle empty email specifically
            if not form.email.data:
                form.email.data = None
            
            # Populate the client object with form data
            form.populate_obj(client)
            
            # Set the assigned user
            client.assigned_user_id = current_user.id
            
            # Ensure required fields are set
            client.estatus = 'activo'  # Set default status
            
            print(f"Creating new client: {client.nombre} {client.apellido_paterno}")
            print(f"Status: {client.estatus}")
            print(f"Celular: {client.celular}")
            print(f"Assigned to: {client.assigned_user_id}")
            
            db.session.add(client)
            db.session.commit()
            
            print(f"Client created successfully with ID: {client.id}")
            flash('Cliente creado exitosamente.', 'success')
            return redirect(url_for('clients.view', id=client.id))
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError creating client: {str(e)}")
            flash('Error al crear el cliente. El email ya existe.', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"Error creating client: {str(e)}")
            flash('Error al crear el cliente. Por favor intente nuevamente.', 'error')
    else:
        print("Form validation errors:", form.errors)
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
    db.session.commit()
    flash('Cliente eliminado exitosamente.', 'success')
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
    db.session.commit()
    
    return jsonify({'success': True})

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
    db.session.commit()
    flash(f'Cliente asignado exitosamente a {new_user.nombre_completo}.', 'success')
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
