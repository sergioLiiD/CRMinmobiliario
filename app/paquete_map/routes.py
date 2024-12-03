from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import jsonify, request, abort, current_app, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from . import map_bp
from .models import MapLocation, MapImage, LotStatus, db
from .forms import MapLocationForm, MapImageUploadForm
from app.properties.models import Lote, Paquete, Fraccionamiento
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from app.auth.routes import admin_required
from app.clients.models import Client
import traceback
from flask import make_response

@map_bp.route('/api/locations', methods=['GET'])
def get_all_locations():
    """
    Retrieve all map locations
    """
    locations = MapLocation.query.all()
    return jsonify([location.to_dict() for location in locations])

@map_bp.route('/api/location/<int:lot_id>', methods=['GET'])
def get_location_by_lot(lot_id):
    """
    Retrieve map location for a specific lot
    """
    location = MapLocation.query.filter_by(lot_id=lot_id).first()
    if not location:
        return jsonify({'message': 'Location not found'}), 404
    return jsonify(location.to_dict())

@map_bp.route('/api/location', methods=['POST'])
def create_location():
    """
    Create a new map location
    """
    form = MapLocationForm(request.form)
    if form.validate():
        # Check if lot exists
        lot = Lote.query.get(form.lot_id.data)
        if not lot:
            return jsonify({'message': 'Lot not found'}), 404
        
        # Check if location already exists
        existing_location = MapLocation.query.filter_by(lot_id=form.lot_id.data).first()
        if existing_location:
            return jsonify({'message': 'Location for this lot already exists'}), 400
        
        new_location = MapLocation(
            lot_id=form.lot_id.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            description=form.description.data
        )
        
        db.session.add(new_location)
        db.session.commit()
        
        return jsonify(new_location.to_dict()), 201
    
    return jsonify({'errors': form.errors}), 400

@map_bp.route('/api/location/<int:lot_id>', methods=['PUT'])
def update_location(lot_id):
    """
    Update an existing map location
    """
    location = MapLocation.query.filter_by(lot_id=lot_id).first()
    if not location:
        return jsonify({'message': 'Location not found'}), 404
    
    form = MapLocationForm(request.form)
    if form.validate():
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        location.description = form.description.data
        
        # Validate status is a valid enum value
        try:
            status_enum = LotStatus[form.status.data.upper()]
        except KeyError:
            current_app.logger.error(f"Invalid status value: {form.status.data}")
            return jsonify({
                'message': f'Invalid status value. Must be one of {list(LotStatus.__members__.keys())}',
                'received_value': form.status.data
            }), 400
        
        # Update location status using validated enum
        location.status = status_enum
        
        db.session.commit()
        
        return jsonify(location.to_dict())
    
    return jsonify({'errors': form.errors}), 400

@map_bp.route('/api/location/<int:lot_id>', methods=['DELETE'])
def delete_location(lot_id):
    """
    Delete a map location
    """
    location = MapLocation.query.filter_by(lot_id=lot_id).first()
    if not location:
        return jsonify({'message': 'Location not found'}), 404
    
    db.session.delete(location)
    db.session.commit()
    
    return jsonify({'message': 'Location deleted successfully'}), 200

@map_bp.route('/api/map/upload', methods=['POST'])
def upload_map_image():
    """
    Upload a new map image
    """
    form = MapImageUploadForm()
    if form.validate_on_submit():
        file = form.map_file.data
        filename = secure_filename(file.filename)
        
        # Determine upload path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        map_upload_path = os.path.join(upload_folder, 'maps')
        os.makedirs(map_upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(map_upload_path, filename)
        file.save(file_path)
        
        # Create MapImage record
        is_active = form.is_active.data == 'true'
        
        # If setting as active, deactivate other maps
        if is_active:
            MapImage.query.update({MapImage.is_active: False})
        
        new_map = MapImage(
            filename=filename,
            is_active=is_active
        )
        
        db.session.add(new_map)
        db.session.commit()
        
        return jsonify(new_map.to_dict()), 201
    
    return jsonify({'errors': form.errors}), 400

@map_bp.route('/api/map/active', methods=['GET'])
def get_active_map():
    """
    Retrieve the currently active map
    """
    active_map = MapImage.query.filter_by(is_active=True).first()
    if not active_map:
        return jsonify({'message': 'No active map found'}), 404
    
    return jsonify(active_map.to_dict())

@map_bp.route('/api/map/location', methods=['POST'])
def create_map_location():
    """
    Create a new map location for a lot
    """
    try:
        # Validate form
        form = MapLocationForm(request.form)
        
        # Explicitly set status choices to match enum
        form.status.choices = [
            ('Libre', 'Libre'), 
            ('Apartado', 'Apartado'), 
            ('Titulado', 'Titulado')
        ]
        
        if form.validate():
            # Normalize status 
            status = normalize_lot_status(form.status.data)
            
            # Find the lot
            lot = Lote.query.get(form.lot_id.data)
            if not lot:
                current_app.logger.error(f"Lot not found: {form.lot_id.data}")
                return jsonify({
                    'error': True, 
                    'message': 'Invalid lot selected',
                    'errors': {'lot_id': ['Lot not found']}
                }), 400
            
            # Find the active map
            map_image = MapImage.query.filter_by(is_active=True).first()
            if not map_image:
                current_app.logger.error("No active map found")
                return jsonify({
                    'error': True, 
                    'message': 'No active map found'
                }), 400
            
            # Check if location already exists
            existing_location = MapLocation.query.filter_by(
                lot_id=lot.id, 
                map_image_id=map_image.id
            ).first()
            
            if existing_location:
                current_app.logger.warning(f"Location already exists for lot {lot.id} on map {map_image.id}")
                return jsonify({
                    'error': True, 
                    'message': 'Location already exists for this lot'
                }), 400
            
            # Create new map location
            try:
                new_location = MapLocation(
                    lot_id=lot.id,
                    map_image_id=map_image.id,
                    x_coordinate=form.x_coordinate.data,
                    y_coordinate=form.y_coordinate.data,
                    status=status  # Now a string
                )
                
                # Update lot status
                lot.estado_del_inmueble = status
                
                # Save to database
                db.session.add(new_location)
                db.session.commit()
                
                # Return JSON response
                return jsonify({
                    'id': new_location.id,
                    'lot_id': lot.id,
                    'x_coordinate': new_location.x_coordinate,
                    'y_coordinate': new_location.y_coordinate,
                    'status': new_location.status
                }), 201
            
            except Exception as db_error:
                db.session.rollback()
                current_app.logger.error(f"Database error creating map location: {db_error}", exc_info=True)
                return jsonify({
                    'error': True, 
                    'message': f'Database error: {str(db_error)}'
                }), 500
        
        # If form validation fails
        current_app.logger.error(f"Form validation failed: {form.errors}")
        
        # Construct detailed error messages
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list
        
        return jsonify({
            'error': True,
            'message': 'Form validation failed',
            'errors': errors
        }), 400
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_map_location: {str(e)}", exc_info=True)
        return jsonify({
            'error': True, 
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@map_bp.route('/api/map/locations', methods=['GET'])
def get_map_locations():
    """
    Retrieve all map locations for the active map
    """
    active_map = MapImage.query.filter_by(is_active=True).first()
    if not active_map:
        return jsonify({'message': 'No active map found'}), 404
    
    locations = MapLocation.query.filter_by(map_image_id=active_map.id).all()
    return jsonify([location.to_dict() for location in locations])

@map_bp.route('/api/map/location/<int:lot_id>', methods=['PUT'])
def update_map_location(lot_id):
    """
    Update an existing map location's status
    """
    active_map = MapImage.query.filter_by(is_active=True).first()
    if not active_map:
        return jsonify({'message': 'No active map found'}), 404
    
    location = MapLocation.query.filter_by(
        lot_id=lot_id, 
        map_image_id=active_map.id
    ).first()
    
    if not location:
        return jsonify({'message': 'Location not found'}), 404
    
    form = MapLocationForm()
    if form.validate_on_submit():
        location.x_coordinate = form.x_coordinate.data
        location.y_coordinate = form.y_coordinate.data
        
        # Validate status is a valid enum value
        try:
            status_enum = LotStatus[form.status.data.upper()]
        except KeyError:
            current_app.logger.error(f"Invalid status value: {form.status.data}")
            return jsonify({
                'message': f'Invalid status value. Must be one of {list(LotStatus.__members__.keys())}',
                'received_value': form.status.data
            }), 400
        
        # Update location status using validated enum
        location.status = status_enum
        
        db.session.commit()
        
        return jsonify(location.to_dict())
    
    return jsonify({'errors': form.errors}), 400

@map_bp.route('/api/paquetes/<int:fraccionamiento_id>', methods=['GET'])
def get_paquetes(fraccionamiento_id):
    """
    Get paquetes for a specific fraccionamiento
    """
    paquetes = Paquete.query.filter_by(fraccionamiento_id=fraccionamiento_id).all()
    return jsonify([
        {
            'id': p.id, 
            'nombre': p.nombre
        } for p in paquetes
    ])

@map_bp.route('/api/lots/<int:paquete_id>', methods=['GET'])
def get_available_lots(paquete_id):
    """
    Get all lots for a specific paquete, including their current status
    """
    lots = Lote.query.filter_by(paquete_id=paquete_id).all()
    
    lots_data = []
    for lot in lots:
        lots_data.append({
            'id': lot.id,
            'manzana': lot.manzana,
            'lote': lot.lote,
            'estado_del_inmueble': lot.estado_del_inmueble
        })
    
    return jsonify(lots_data)

@map_bp.route('/api/lots/<int:paquete_id>/<status>', methods=['GET'])
def get_lots_by_status(paquete_id, status):
    """
    Get lots for a specific paquete filtered by status
    """
    # Normalize status to title case for comparison
    normalized_status = status.lower().capitalize()
    
    # Log the incoming parameters
    current_app.logger.info(f"Fetching lots for paquete {paquete_id} with status {status}")
    current_app.logger.info(f"Normalized status: {normalized_status}")
    
    # Find all lots for the paquete first
    all_lots = Lote.query.filter_by(paquete_id=paquete_id).all()
    current_app.logger.info(f"Total lots in paquete: {len(all_lots)}")
    
    # Filter lots by status, allowing for case-insensitive matching
    lots = [lot for lot in all_lots if lot.estado_del_inmueble.lower() == normalized_status.lower()]
    current_app.logger.info(f"Lots matching status {status}: {len(lots)}")
    
    lots_data = []
    for lot in lots:
        lots_data.append({
            'id': lot.id,
            'manzana': lot.manzana,
            'lote': lot.lote,
            'estado_del_inmueble': lot.estado_del_inmueble
        })
    
    # Log the data being returned
    current_app.logger.info(f"Returning {len(lots_data)} lots")
    
    return jsonify(lots_data)

@map_bp.route('/api/lot_statuses', methods=['GET'])
def get_lot_statuses():
    """
    API endpoint to retrieve all valid lot statuses
    """
    try:
        # Return all possible lot statuses
        statuses = [
            {
                'value': status,
                'label': status,
                'description': f'Lot is {status.lower()}'
            } for status in ['Libre', 'Apartado', 'Titulado']
        ]
        return jsonify(statuses)
    except Exception as e:
        current_app.logger.error(f"Error fetching lot statuses: {str(e)}")
        return jsonify({'error': 'Could not fetch lot statuses'}), 500

def normalize_lot_status(status):
    """
    Normalize lot status to a consistent format
    """
    status_mapping = {
        'libre': 'Libre',
        'LIBRE': 'Libre',
        'Libre': 'Libre',
        'apartado': 'Apartado',
        'APARTADO': 'Apartado',
        'Apartado': 'Apartado',
        'titulado': 'Titulado',
        'TITULADO': 'Titulado',
        'Titulado': 'Titulado',
        'lib': 'Libre',
        'LIB': 'Libre',
        'Li': 'Libre',
        'ap': 'Apartado',
        'AP': 'Apartado',
        'Ap': 'Apartado',
        'ti': 'Titulado',
        'TI': 'Titulado',
        'Ti': 'Titulado',
        'disponible': 'Libre',
        'DISPONIBLE': 'Libre',
        'Disponible': 'Libre',
        'vendido': 'Titulado',
        'VENDIDO': 'Titulado',
        'Vendido': 'Titulado',
        'reservado': 'Apartado',
        'RESERVADO': 'Apartado',
        'Reservado': 'Apartado'
    }
    
    # Handle None or empty input
    if not status:
        return 'Libre'
    
    # Convert to string and strip whitespace
    status_str = str(status).strip()
    
    # Return mapped status or default to Libre
    return status_mapping.get(status_str, 'Libre')

@map_bp.route('/api/map_locations', methods=['GET'])
def get_all_map_locations():
    """
    API endpoint to retrieve all map locations with normalized status
    """
    try:
        # Query all map locations with associated lot information
        map_locations = MapLocation.query.all()
        
        # Prepare map locations data with normalized status
        locations_data = [
            {
                'id': location.id,
                'x_coordinate': location.x_coordinate,
                'y_coordinate': location.y_coordinate,
                'lot': {
                    'id': location.lote.id if location.lote else None,
                    'manzana': location.lote.manzana if location.lote else None,
                    'lote': location.lote.lote if location.lote else None,
                    'status': location.lote.estado_del_inmueble if location.lote else None,
                    'normalized_status': normalize_lot_status(location.lote.estado_del_inmueble) if location.lote else None,
                    'fraccionamiento': location.lote.fraccionamiento.nombre if location.lote and location.lote.fraccionamiento else None
                },
                'map_image': {
                    'id': location.map_image.id if location.map_image else None,
                    'filename': location.map_image.filename if location.map_image else None
                }
            } for location in map_locations
        ]
        
        return jsonify(locations_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching map locations: {str(e)}")
        return jsonify({'error': 'Could not fetch map locations'}), 500

@map_bp.route('/api/map_location_statuses', methods=['GET'])
def get_map_location_statuses():
    """
    API endpoint to retrieve map location statuses with detailed information
    """
    try:
        # Query map locations with their lot statuses
        map_locations = MapLocation.query.all()
        
        # Prepare status data
        status_data = [
            {
                'map_location_id': location.id,
                'lot_id': location.lote.id if location.lote else None,
                'original_status': location.lote.estado_del_inmueble if location.lote else None,
                'normalized_status': normalize_lot_status(location.lote.estado_del_inmueble) if location.lote else None,
                'fraccionamiento': location.lote.fraccionamiento.nombre if location.lote and location.lote.fraccionamiento else None
            } for location in map_locations
        ]
        
        return jsonify(status_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching map location statuses: {str(e)}")
        return jsonify({'error': 'Could not fetch map location statuses'}), 500

@map_bp.route('/api/lot/<int:lot_id>', methods=['GET'])
def get_lot_details(lot_id):
    """
    API endpoint to retrieve detailed information for a specific lot
    """
    try:
        # Verify database connection and model
        if not hasattr(Lote, 'query'):
            current_app.logger.error("Lote model is not properly configured")
            return jsonify({
                'error': True, 
                'message': 'Database model not configured correctly'
            }), 500

        # Find the lot with more detailed query
        lot = Lote.query.options(
            joinedload(Lote.paquete).joinedload(Paquete.fraccionamiento)
        ).get(lot_id)
        
        # Log additional details for debugging
        current_app.logger.info(f"Attempting to fetch lot with ID: {lot_id}")
        current_app.logger.info(f"Total lots in database: {Lote.query.count()}")
        
        if not lot:
            current_app.logger.warning(f"Lot not found: {lot_id}")
            return jsonify({
                'error': True, 
                'message': f'Lot with ID {lot_id} not found',
                'fallback_status': 'Libre'  # Provide a default status
            }), 404
        
        # Prepare lot details with more comprehensive information
        lot_details = {
            'id': lot.id,
            'lote_numero': lot.lote,
            'manzana': lot.manzana,
            'fraccionamiento': lot.paquete.fraccionamiento.nombre if lot.paquete and lot.paquete.fraccionamiento else None,
            'paquete': lot.paquete.nombre if lot.paquete else None,
            'fraccionamiento_id': lot.paquete.fraccionamiento.id if lot.paquete and lot.paquete.fraccionamiento else None,
            'paquete_id': lot.paquete_id,
            'estado_del_inmueble': normalize_lot_status(lot.estado_del_inmueble),
            'superficie': float(lot.terreno) if lot.terreno else None,
            'precio': float(lot.precio) if lot.precio else None
        }
        
        return jsonify(lot_details)
    
    except Exception as e:
        # More detailed error logging
        import traceback
        error_message = f"Error fetching lot details for lot {lot_id}: {str(e)}"
        current_app.logger.error(error_message)
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            'error': True, 
            'message': error_message,
            'fallback_status': 'Libre',
            'traceback': traceback.format_exc()
        }), 500

@login_required
@admin_required
def admin_map_upload():
    """
    Admin page for uploading map images
    """
    form = MapImageUploadForm()
    
    if form.validate_on_submit():
        file = form.map_file.data
        filename = secure_filename(file.filename)
        
        # Determine upload path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        map_upload_path = os.path.join(upload_folder, 'maps')
        os.makedirs(map_upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(map_upload_path, filename)
        file.save(file_path)
        
        # Create MapImage record
        is_active = form.is_active.data == 'true'
        
        # If setting as active, deactivate other maps
        if is_active:
            MapImage.query.update({MapImage.is_active: False})
        
        new_map = MapImage(
            filename=filename,
            is_active=is_active
        )
        
        db.session.add(new_map)
        db.session.commit()
        
        flash('Map image uploaded successfully!', 'success')
        return redirect(url_for('map.admin_map_upload'))
    
    # Get existing map images
    existing_maps = MapImage.query.order_by(MapImage.upload_date.desc()).all()
    
    return render_template('map/admin_map_upload.html', form=form, existing_maps=existing_maps)

@login_required
@admin_required
def admin_map_lots():
    """
    Admin page for placing lots on the map
    """
    try:
        # Prepare form with dynamic choices
        form = MapLocationForm()
        
        # Use string-based status choices
        form.status.choices = [
            ('Libre', 'Libre'), 
            ('Apartado', 'Apartado'), 
            ('Titulado', 'Titulado')
        ]
        
        # Populate fraccionamiento choices
        fraccionamientos = Fraccionamiento.query.order_by(Fraccionamiento.nombre).all()
        form.fraccionamiento.choices = [(None, 'Select Fraccionamiento')] + [
            (f.id, f.nombre) for f in fraccionamientos
        ]
        
        # Get active map
        map_image = MapImage.query.filter_by(is_active=True).first()
        
        # Prepare existing locations, handling potential status variations
        existing_locations = []
        if map_image:
            # Fetch locations, converting statuses to a consistent format
            raw_locations = MapLocation.query.filter_by(map_image_id=map_image.id).all()
            
            # Normalize location statuses
            for loc in raw_locations:
                # Ensure status is a consistent string
                if hasattr(loc, 'status'):
                    # If status is an enum, convert to string
                    if hasattr(loc.status, 'name'):
                        loc.status = loc.status.name
                    
                    # Normalize status
                    loc.status = normalize_lot_status(loc.status)
            
            existing_locations = raw_locations
        
        return render_template('map/admin_map_lots.html', 
                               active_map=map_image, 
                               form=form,
                               existing_locations=existing_locations)
    
    except Exception as e:
        current_app.logger.error(f"Error in admin_map_lots: {str(e)}", exc_info=True)
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('map/admin_map_lots.html', 
                               active_map=None, 
                               form=None,
                               existing_locations=[]), 500

@map_bp.route('/api/clients', methods=['GET'])
def get_clients():
    """
    API endpoint to retrieve all clients with basic information
    """
    try:
        # Query all clients with basic details
        clients = Client.query.all()
        
        # Prepare client data
        clients_data = [
            {
                'id': client.id,
                'nombre_completo': client.nombre_completo,
                'email': client.email,
                'celular': client.celular,
                'estatus': client.estatus,
                'ciudad': client.ciudad,
                'estado': client.estado
            } for client in clients
        ]
        
        return jsonify(clients_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching clients: {str(e)}")
        return jsonify({'error': 'Could not fetch clients'}), 500

@map_bp.route('/api/client/<int:client_id>', methods=['GET'])
def get_client_details(client_id):
    """
    API endpoint to retrieve detailed information for a specific client
    """
    try:
        # Find the client by ID
        client = Client.query.get_or_404(client_id)
        
        # Prepare comprehensive client details
        client_details = {
            # Personal Information
            'id': client.id,
            'nombre_completo': client.nombre_completo,
            'nombre': client.nombre,
            'apellido_paterno': client.apellido_paterno,
            'apellido_materno': client.apellido_materno,
            'fecha_nacimiento': str(client.fecha_nacimiento) if client.fecha_nacimiento else None,
            'sexo': client.sexo,
            'estado_civil': client.estado_civil,
            'nacionalidad': client.nacionalidad,
            
            # Contact Information
            'email': client.email,
            'celular': client.celular,
            'direccion': client.direccion,
            'ciudad': client.ciudad,
            'estado': client.estado,
            'codigo_postal': client.codigo_postal,
            
            # Professional Information
            'nombre_empresa': client.nombre_empresa,
            'puesto': client.puesto,
            'ingresos': float(client.ingresos) if client.ingresos else None,
            
            # Status and Metadata
            'estatus': client.estatus,
            'fecha_registro': str(client.fecha_registro) if client.fecha_registro else None,
            'fecha_ultimo_contacto': str(client.fecha_ultimo_contacto) if client.fecha_ultimo_contacto else None,
            
            # Related Lots
            'lots': []
        }
        
        # Fetch lots associated with this client
        lots = Lote.query.filter_by(cliente_id=client_id).all()
        client_details['lots'] = [
            {
                'id': lot.id,
                'manzana': lot.manzana,
                'lote': lot.lote,
                'fraccionamiento': lot.fraccionamiento.nombre if lot.fraccionamiento else None,
                'estado_del_inmueble': lot.estado_del_inmueble,
                'precio': float(lot.precio) if lot.precio else None
            } for lot in lots
        ]
        
        return jsonify(client_details)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching client details for client {client_id}: {str(e)}")
        return jsonify({'error': 'Could not fetch client details'}), 500

@map_bp.route('/api/client/<int:client_id>/lots', methods=['GET'])
def get_client_lots(client_id):
    """
    API endpoint to retrieve lots associated with a specific client
    """
    try:
        # Find the client by ID
        client = Client.query.get_or_404(client_id)
        
        # Fetch lots associated with this client
        lots = Lote.query.filter_by(cliente_id=client_id).all()
        
        # Prepare lot data
        lots_data = [
            {
                'id': lot.id,
                'manzana': lot.manzana,
                'lote': lot.lote,
                'fraccionamiento': lot.fraccionamiento.nombre if lot.fraccionamiento else None,
                'paquete': lot.paquete.nombre if lot.paquete else None,
                'estado_del_inmueble': lot.estado_del_inmueble,
                'precio': float(lot.precio) if lot.precio else None,
                'superficie': float(lot.superficie) if lot.superficie else None,
                'map_location': {
                    'x_coordinate': lot.map_location.x_coordinate if lot.map_location else None,
                    'y_coordinate': lot.map_location.y_coordinate if lot.map_location else None,
                    'map_image': lot.map_location.map_image.filename if lot.map_location and lot.map_location.map_image else None
                } if lot.map_location else None
            } for lot in lots
        ]
        
        return jsonify(lots_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching lots for client {client_id}: {str(e)}")
        return jsonify({'error': 'Could not fetch client lots'}), 500

@map_bp.route('/api/map-location-api', methods=['POST'])
@login_required
def create_api_map_location():
    """
    Create a new map location for a lot via API
    """
    # Ensure user is authenticated
    if not current_user.is_authenticated:
        current_app.logger.warning(f"Unauthenticated access attempt by {request.remote_addr}")
        return jsonify({
            'error': True,
            'message': 'Authentication required'
        }), 401

    # Ensure request is JSON
    if not request.is_json:
        current_app.logger.warning(f"Non-JSON request from {request.remote_addr}")
        return jsonify({
            'error': True,
            'message': 'Request must be JSON'
        }), 400

    # Log the full request data for debugging
    current_app.logger.info(f"Received map location request from {current_user.username}: {request.get_json()}")

    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate that data is not None
        if data is None:
            current_app.logger.error(f"Empty request body from {current_user.username}")
            return jsonify({
                'error': True,
                'message': 'Empty request body'
            }), 400
        
        # Validate required fields with more detailed error handling
        required_fields = ['lot_id', 'x_coordinate', 'y_coordinate', 'status']
        for field in required_fields:
            if field not in data or data[field] is None:
                current_app.logger.warning(f"Missing required field {field} from {current_user.username}")
                return jsonify({
                    'error': True,
                    'message': f'Missing or invalid required field: {field}',
                    'received_data': data
                }), 400
        
        # Validate lot_id is an integer
        try:
            lot_id = int(data['lot_id'])
        except (ValueError, TypeError):
            current_app.logger.warning(f"Invalid lot_id from {current_user.username}: {data['lot_id']}")
            return jsonify({
                'error': True,
                'message': 'Invalid lot_id. Must be an integer.',
                'received_lot_id': data['lot_id']
            }), 400
        
        # Retrieve the lot
        lot = Lote.query.get(lot_id)
        if not lot:
            current_app.logger.warning(f"Lot with ID {lot_id} not found for user {current_user.username}")
            return jsonify({
                'error': True,
                'message': f'Lot with ID {lot_id} not found',
                'available_lots': [l.id for l in Lote.query.all()]
            }), 404
        
        # Validate coordinates
        try:
            x_coordinate = float(data['x_coordinate'])
            y_coordinate = float(data['y_coordinate'])
            
            # Optional: Add coordinate range validation if needed
            if not (0 <= x_coordinate <= 100 and 0 <= y_coordinate <= 100):
                raise ValueError("Coordinates must be between 0 and 100")
        except (ValueError, TypeError) as e:
            current_app.logger.warning(f"Invalid coordinates from {current_user.username}: {e}")
            return jsonify({
                'error': True,
                'message': f'Invalid coordinates: {str(e)}',
                'received_coordinates': {
                    'x': data['x_coordinate'],
                    'y': data['y_coordinate']
                }
            }), 400
        
        # Normalize status
        try:
            normalized_status = normalize_lot_status(data['status'])
        except Exception as e:
            current_app.logger.warning(f"Error normalizing status from {current_user.username}: {e}")
            return jsonify({
                'error': True,
                'message': f'Error normalizing status: {str(e)}',
                'received_status': data['status']
            }), 400
        
        # Find the active map image
        active_map_image = MapImage.query.filter_by(is_active=True).first()
        if not active_map_image:
            current_app.logger.warning(f"No active map image found for lot {lot_id}")
            return jsonify({
                'error': True,
                'message': 'No active map image available'
            }), 400
        
        # Check if a map location already exists for this lot
        existing_location = MapLocation.query.filter_by(lot_id=lot_id).first()
        
        if existing_location:
            # Update existing location
            existing_location.x_coordinate = x_coordinate
            existing_location.y_coordinate = y_coordinate
            existing_location.status = normalized_status
            existing_location.map_image_id = active_map_image.id
            db.session.commit()
            
            current_app.logger.info(f"Updated map location for lot {lot_id} by user {current_user.id}")
            
            return jsonify({
                'message': 'Map location updated successfully',
                'location': {
                    'lot_id': existing_location.lot_id,
                    'x_coordinate': existing_location.x_coordinate,
                    'y_coordinate': existing_location.y_coordinate,
                    'status': existing_location.status
                }
            }), 200
        
        # Create new map location
        new_location = MapLocation(
            lot_id=lot_id,
            map_image_id=active_map_image.id,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            status=normalized_status
        )
        
        # Add to database
        db.session.add(new_location)
        db.session.commit()
        
        # Log the map location creation
        current_app.logger.info(f"Map location created for lot {lot_id} at ({x_coordinate}, {y_coordinate}) by {current_user.username}")
        
        return jsonify({
            'message': 'Map location created successfully',
            'location': {
                'lot_id': new_location.lot_id,
                'x_coordinate': new_location.x_coordinate,
                'y_coordinate': new_location.y_coordinate,
                'status': new_location.status
            }
        }), 201
    
    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        
        # Log the error
        current_app.logger.error(f"Unexpected error creating map location for {current_user.username}: {str(e)}", exc_info=True)
        
        return jsonify({
            'error': True,
            'message': f'An unexpected error occurred: {str(e)}',
            'traceback': str(traceback.format_exc())
        }), 500

@map_bp.route('/get-csrf-token', methods=['GET'])
@login_required
def get_csrf_token():
    """
    Endpoint to retrieve CSRF token for AJAX requests
    """
    csrf_token = generate_csrf()
    response = make_response(jsonify({'csrf_token': csrf_token}))
    return response

@map_bp.route('/api/map-location-api/delete/<int:lot_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_map_location(lot_id):
    """
    Delete a map location for a specific lot
    """
    try:
        # Find the map location for the given lot
        map_location = MapLocation.query.filter_by(lot_id=lot_id).first()
        
        if not map_location:
            return jsonify({
                'error': True, 
                'message': f'No map location found for lot {lot_id}'
            }), 404
        
        # Delete the map location
        db.session.delete(map_location)
        db.session.commit()
        
        # Log the deletion
        current_app.logger.info(f"Map location for lot {lot_id} deleted by user {current_user.id}")
        
        return jsonify({
            'success': True, 
            'message': f'Lot {lot_id} removed from map successfully'
        }), 200
    
    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        
        # Log the error
        current_app.logger.error(f"Error deleting map location for lot {lot_id}: {str(e)}")
        
        return jsonify({
            'error': True, 
            'message': f'Error removing lot {lot_id} from map: {str(e)}'
        }), 500

map_bp.add_url_rule('/admin/map-upload', view_func=admin_map_upload, methods=['GET', 'POST'])
map_bp.add_url_rule('/admin/map-lots', view_func=admin_map_lots, methods=['GET'])
