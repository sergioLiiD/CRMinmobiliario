import os
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import bp
from .forms import PrototipoForm, FraccionamientoForm, PaqueteForm, LoteForm, LoteBulkUploadForm, LoteFilterForm
from .models import Prototipo, PrototipoImagen, Fraccionamiento, Paquete, Lote, LoteAsignacion
from app.clients.models import Client
from app.database import db
from app.auth.decorators import admin_required
from app.auth.models import UserRole
import csv
import io
import traceback
from datetime import datetime

def allowed_file(filename):
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def check_file_size(file):
    """Check if file size is within allowed limit"""
    file.seek(0, 2)  # Seek to end of file
    size = file.tell()  # Get current position (file size)
    file.seek(0)  # Reset file position
    return size <= current_app.config['MAX_FILE_SIZE']

def handle_image_upload(file, prototipo_id):
    """Handle the upload of a single image file"""
    if not file or not file.filename:
        raise ValueError("No se proporcionó ningún archivo")
        
    if not allowed_file(file.filename):
        raise ValueError(f"Tipo de archivo no permitido: {file.filename}")
    
    if not check_file_size(file):
        max_size_mb = current_app.config['MAX_FILE_SIZE'] / (1024 * 1024)
        raise ValueError(f"El archivo {file.filename} excede el tamaño máximo permitido de {max_size_mb}MB")
    
    try:
        filename = secure_filename(file.filename)
        filename = f"{prototipo_id}_{filename}"
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'prototipos')
        filepath = os.path.join(upload_dir, filename)
        
        # Save the file
        file.save(filepath)
        
        # Verify file was saved successfully
        if not os.path.exists(filepath):
            raise IOError(f"No se pudo guardar el archivo en: {filepath}")
        
        # Create database record
        img = PrototipoImagen(
            prototipo_id=prototipo_id,
            filename=filename
        )
        db.session.add(img)
        
        return img
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)  # Clean up file if database operation fails
        raise IOError(f"Error al procesar archivo {file.filename}: {str(e)}")

@bp.route('/properties/prototipos')
@login_required
def prototipos_index():
    prototipos = Prototipo.query.order_by(Prototipo.nombre_prototipo).all()
    return render_template('properties/prototipos/index.html', prototipos=prototipos)

@bp.route('/properties/prototipos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def prototipo_nuevo():
    print("\n=== New Prototype Form Submission ===")
    print("Request Method:", request.method)
    print("Form Data:", request.form)
    print("Files:", request.files)
    print("Headers:", request.headers)
    
    form = PrototipoForm()
    
    if form.validate_on_submit():
        print("Form validated successfully")
        try:
            prototipo = Prototipo(
                nombre_prototipo=form.nombre_prototipo.data,
                superficie_terreno=form.superficie_terreno.data,
                superficie_construccion=form.superficie_construccion.data,
                niveles=form.niveles.data,
                recamaras=form.recamaras.data,
                banos=form.banos.data,
                observaciones=form.observaciones.data,
                precio=form.precio.data
            )
            print("Created Prototipo object:", prototipo.__dict__)
            
            db.session.add(prototipo)
            db.session.commit()
            print("Saved Prototipo to database with ID:", prototipo.id)

            if form.imagenes.data:
                print("Processing images...")
                for imagen in form.imagenes.data:
                    if imagen and allowed_file(imagen.filename):
                        filename = secure_filename(imagen.filename)
                        filename = f"{prototipo.id}_{filename}"
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'prototipos', filename)
                        print(f"Saving image to: {filepath}")
                        imagen.save(filepath)
                        
                        img = PrototipoImagen(
                            prototipo_id=prototipo.id,
                            filename=filename
                        )
                        db.session.add(img)
                db.session.commit()
                print("Images saved successfully")

            flash('Prototipo creado exitosamente.', 'success')
            return redirect(url_for('properties.prototipos_index'))
        except Exception as e:
            print("Error saving prototipo:", str(e))
            db.session.rollback()
            flash('Error al guardar el prototipo: ' + str(e), 'danger')
    else:
        print("GET request - displaying form")
    
    return render_template('properties/prototipos/form.html', form=form, title='Nuevo Prototipo')

@bp.route('/properties/prototipos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def prototipo_editar(id):
    print("\n=== Edit Prototype Form Submission ===")
    print("Request Method:", request.method)
    
    prototipo = Prototipo.query.get_or_404(id)
    form = PrototipoForm(obj=prototipo)
    
    if form.validate_on_submit():
        print("Form validated successfully")
        try:
            # Update basic information
            form.populate_obj(prototipo)
            print("Basic information updated")
            
            # Handle new images
            files = request.files.getlist('imagenes')
            if files and files[0].filename:
                print(f"\nProcessing {len(files)} files...")
                
                # Calculate total size of all files
                total_size = 0
                for file in files:
                    file.seek(0, 2)  # Seek to end
                    total_size += file.tell()
                    file.seek(0)  # Reset position
                
                # Check if total size exceeds MAX_CONTENT_LENGTH
                if total_size > current_app.config['MAX_CONTENT_LENGTH']:
                    max_size_mb = current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
                    raise ValueError(f"El tamaño total de los archivos ({total_size / (1024 * 1024):.1f}MB) excede el límite permitido de {max_size_mb}MB")
                
                # Process each file
                for file in files:
                    try:
                        img = handle_image_upload(file, prototipo.id)
                        print(f"Successfully processed file: {file.filename}")
                    except (ValueError, IOError) as e:
                        flash(str(e), 'warning')
                        continue
            
            db.session.commit()
            flash('Prototipo actualizado exitosamente.', 'success')
            return redirect(url_for('properties.prototipos_index'))
            
        except Exception as e:
            print("Error updating prototipo:", str(e))
            db.session.rollback()
            flash('Error al actualizar el prototipo: ' + str(e), 'danger')
    else:
        if request.method == 'POST':
            print("Form validation failed")
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en {field}: {error}', 'danger')
    
    # Get current images for display
    imagenes = PrototipoImagen.query.filter_by(prototipo_id=id).all()
    return render_template('properties/prototipos/form.html', 
                         form=form, 
                         prototipo=prototipo,
                         imagenes=imagenes,
                         title='Editar Prototipo')

@bp.route('/properties/prototipos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def prototipo_eliminar(id):
    print("Handling prototipo_eliminar request")
    prototipo = Prototipo.query.get_or_404(id)
    
    # Delete associated images from filesystem
    for imagen in prototipo.imagenes:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'prototipos', imagen.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(prototipo)
    db.session.commit()
    print("Prototipo deleted successfully")
    
    flash('Prototipo eliminado exitosamente.', 'success')
    return redirect(url_for('properties.prototipos_index'))

@bp.route('/properties/prototipos/imagen/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def prototipo_imagen_eliminar(id):
    print(f"\n=== Deleting Image {id} ===")
    imagen = PrototipoImagen.query.get_or_404(id)
    prototipo_id = imagen.prototipo_id
    
    try:
        # Delete file from filesystem
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'prototipos', imagen.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted file: {filepath}")
        
        # Delete database record
        db.session.delete(imagen)
        db.session.commit()
        print("Deleted database record")
        
        flash('Imagen eliminada exitosamente.', 'success')
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        db.session.rollback()
        flash('Error al eliminar la imagen: ' + str(e), 'danger')
    
    return redirect(url_for('properties.prototipo_editar', id=prototipo_id))

# Fraccionamiento routes
@bp.route('/properties/fraccionamientos')
@login_required
def fraccionamientos_index():
    fraccionamientos = Fraccionamiento.query.all()
    return render_template('properties/fraccionamientos/index.html', fraccionamientos=fraccionamientos)

@bp.route('/properties/fraccionamientos/new', methods=['GET', 'POST'])
@login_required
def fraccionamiento_new():
    form = FraccionamientoForm()
    if form.validate_on_submit():
        fraccionamiento = Fraccionamiento(
            nombre=form.nombre.data,
            ubicacion=form.ubicacion.data
        )
        
        if form.logo.data:
            logo_filename = secure_filename(form.logo.data.filename)
            logo_path = os.path.join('uploads', 'fraccionamientos', 'logos', logo_filename)
            os.makedirs(os.path.dirname(os.path.join(current_app.static_folder, logo_path)), exist_ok=True)
            form.logo.data.save(os.path.join(current_app.static_folder, logo_path))
            fraccionamiento.logo = logo_path
            
        if form.sembrado.data:
            sembrado_filename = secure_filename(form.sembrado.data.filename)
            sembrado_path = os.path.join('uploads', 'fraccionamientos', 'sembrados', sembrado_filename)
            os.makedirs(os.path.dirname(os.path.join(current_app.static_folder, sembrado_path)), exist_ok=True)
            form.sembrado.data.save(os.path.join(current_app.static_folder, sembrado_path))
            fraccionamiento.sembrado = sembrado_path

        db.session.add(fraccionamiento)
        db.session.commit()
        flash('Fraccionamiento creado exitosamente.', 'success')
        return redirect(url_for('properties.fraccionamientos_index'))
    return render_template('properties/fraccionamientos/form.html', form=form)

@bp.route('/properties/fraccionamientos/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def fraccionamiento_edit(id):
    fraccionamiento = Fraccionamiento.query.get_or_404(id)
    form = FraccionamientoForm(obj=fraccionamiento)
    
    if form.validate_on_submit():
        form.populate_obj(fraccionamiento)
        
        if form.logo.data:
            logo_filename = secure_filename(form.logo.data.filename)
            logo_path = os.path.join('uploads', 'fraccionamientos', 'logos', logo_filename)
            os.makedirs(os.path.dirname(os.path.join(current_app.static_folder, logo_path)), exist_ok=True)
            form.logo.data.save(os.path.join(current_app.static_folder, logo_path))
            fraccionamiento.logo = logo_path
            
        if form.sembrado.data:
            sembrado_filename = secure_filename(form.sembrado.data.filename)
            sembrado_path = os.path.join('uploads', 'fraccionamientos', 'sembrados', sembrado_filename)
            os.makedirs(os.path.dirname(os.path.join(current_app.static_folder, sembrado_path)), exist_ok=True)
            form.sembrado.data.save(os.path.join(current_app.static_folder, sembrado_path))
            fraccionamiento.sembrado = sembrado_path

        db.session.commit()
        flash('Fraccionamiento actualizado exitosamente.', 'success')
        return redirect(url_for('properties.fraccionamientos_index'))
        
    # Pre-populate form fields
    if fraccionamiento.logo:
        form.logo.description = f'Logo actual: {os.path.basename(fraccionamiento.logo)}'
    if fraccionamiento.sembrado:
        form.sembrado.description = f'Sembrado actual: {os.path.basename(fraccionamiento.sembrado)}'
        
    return render_template('properties/fraccionamientos/form.html', 
                         form=form, 
                         fraccionamiento=fraccionamiento)

@bp.route('/properties/fraccionamientos/<int:id>/delete', methods=['POST'])
@login_required
def fraccionamiento_delete(id):
    fraccionamiento = Fraccionamiento.query.get_or_404(id)
    
    # Delete associated files
    if fraccionamiento.logo and os.path.exists(os.path.join(current_app.static_folder, fraccionamiento.logo)):
        os.remove(os.path.join(current_app.static_folder, fraccionamiento.logo))
    if fraccionamiento.sembrado and os.path.exists(os.path.join(current_app.static_folder, fraccionamiento.sembrado)):
        os.remove(os.path.join(current_app.static_folder, fraccionamiento.sembrado))
    
    db.session.delete(fraccionamiento)
    db.session.commit()
    flash('Fraccionamiento eliminado exitosamente.', 'success')
    return redirect(url_for('properties.fraccionamientos_index'))

# Paquete routes
@bp.route('/properties/fraccionamientos/<int:fraccionamiento_id>/paquetes')
@login_required
def paquetes_index(fraccionamiento_id):
    fraccionamiento = Fraccionamiento.query.get_or_404(fraccionamiento_id)
    return render_template('properties/paquetes/index.html', 
                         fraccionamiento=fraccionamiento,
                         paquetes=fraccionamiento.paquetes)

@bp.route('/properties/fraccionamientos/<int:fraccionamiento_id>/paquetes/new', methods=['GET', 'POST'])
@login_required
def paquete_new(fraccionamiento_id):
    fraccionamiento = Fraccionamiento.query.get_or_404(fraccionamiento_id)
    form = PaqueteForm()
    
    if form.validate_on_submit():
        paquete = Paquete(
            nombre=form.nombre.data,
            fraccionamiento_id=fraccionamiento_id
        )
        db.session.add(paquete)
        db.session.commit()
        flash('Paquete creado exitosamente.', 'success')
        return redirect(url_for('properties.paquetes_index', fraccionamiento_id=fraccionamiento_id))
    
    return render_template('properties/paquetes/form.html', 
                         form=form, 
                         fraccionamiento=fraccionamiento)

# Lote routes
@bp.route('/properties/paquetes/<int:paquete_id>/lotes')
@login_required
def lotes_index(paquete_id):
    paquete = Paquete.query.get_or_404(paquete_id)
    return render_template('properties/lotes/index.html', 
                         paquete=paquete,
                         lotes=paquete.lotes)

@bp.route('/properties/paquetes/<int:paquete_id>/lotes/new', methods=['GET', 'POST'])
@login_required
def lote_new(paquete_id):
    paquete = Paquete.query.get_or_404(paquete_id)
    form = LoteForm()
    
    if form.validate_on_submit():
        # Convert empty strings to None for optional fields
        numero_interior = form.numero_interior.data if form.numero_interior.data else None
        cuv = form.cuv.data if form.cuv.data else None
        terreno = form.terreno.data if form.terreno.data else None
        
        # Create new lote with required fields
        lote = Lote(
            paquete_id=paquete_id,
            prototipo_id=form.prototipo_id.data,
            calle=form.calle.data,
            numero_exterior=form.numero_exterior.data,
            numero_interior=numero_interior,
            manzana=form.manzana.data,
            lote=form.lote.data,
            cuv=cuv,
            terreno=terreno,
            tipo_de_lote=form.tipo_de_lote.data,
            estado_del_inmueble=form.estado_del_inmueble.data,
            precio=form.precio.data
        )
        
        # Handle optional orientation fields
        for i in range(1, 5):
            orientacion = getattr(form, f'orientacion_{i}').data
            medidas = getattr(form, f'medidas_orientacion_{i}').data
            colindancia = getattr(form, f'colindancia_{i}').data
            
            # Only set if at least one field in the group is not empty
            if any([orientacion, medidas, colindancia]):
                setattr(lote, f'orientacion_{i}', orientacion if orientacion else None)
                setattr(lote, f'medidas_orientacion_{i}', medidas if medidas else None)
                setattr(lote, f'colindancia_{i}', colindancia if colindancia else None)
        
        db.session.add(lote)
        db.session.commit()
        flash('Lote creado exitosamente.', 'success')
        return redirect(url_for('properties.lotes_index', paquete_id=paquete_id))
        
    return render_template('properties/lotes/form.html', 
                         form=form, 
                         paquete=paquete)

@bp.route('/properties/lotes/<int:lote_id>/edit', methods=['GET', 'POST'])
@login_required
def lote_edit(lote_id):
    lote = Lote.query.get_or_404(lote_id)
    form = LoteForm()
    
    # Get prototipos for the select field through the correct relationship chain
    prototipos = Prototipo.query.join(Lote).join(Paquete).join(Fraccionamiento)\
        .filter(Fraccionamiento.id == lote.paquete.fraccionamiento_id).distinct().all()
    form.prototipo_id.choices = [(p.id, p.nombre_prototipo) for p in prototipos]
    
    if request.method == 'GET':
        form.prototipo_id.data = lote.prototipo_id
        form.calle.data = lote.calle
        form.numero_exterior.data = lote.numero_exterior
        form.numero_interior.data = lote.numero_interior
        form.manzana.data = lote.manzana
        form.lote.data = lote.lote
        form.cuv.data = lote.cuv
        form.terreno.data = lote.terreno
        form.tipo_de_lote.data = lote.tipo_de_lote
        form.estado_del_inmueble.data = lote.estado_del_inmueble
        form.precio.data = lote.precio
        
        # Load orientation data
        for i in range(1, 5):
            getattr(form, f'orientacion_{i}').data = getattr(lote, f'orientacion_{i}')
            getattr(form, f'medidas_orientacion_{i}').data = getattr(lote, f'medidas_orientacion_{i}')
            getattr(form, f'colindancia_{i}').data = getattr(lote, f'colindancia_{i}')
    
    if form.validate_on_submit():
        lote.prototipo_id = form.prototipo_id.data
        lote.calle = form.calle.data
        lote.numero_exterior = form.numero_exterior.data
        lote.numero_interior = form.numero_interior.data if form.numero_interior.data else None
        lote.manzana = form.manzana.data
        lote.lote = form.lote.data
        lote.cuv = form.cuv.data if form.cuv.data else None
        lote.terreno = form.terreno.data if form.terreno.data else None
        lote.tipo_de_lote = form.tipo_de_lote.data
        lote.estado_del_inmueble = form.estado_del_inmueble.data
        lote.precio = form.precio.data
        
        # Update orientation data
        for i in range(1, 5):
            orientacion = getattr(form, f'orientacion_{i}').data
            medidas = getattr(form, f'medidas_orientacion_{i}').data
            colindancia = getattr(form, f'colindancia_{i}').data
            
            setattr(lote, f'orientacion_{i}', orientacion if orientacion else None)
            setattr(lote, f'medidas_orientacion_{i}', medidas if medidas else None)
            setattr(lote, f'colindancia_{i}', colindancia if colindancia else None)
        
        db.session.commit()
        flash('Lote actualizado exitosamente.', 'success')
        return redirect(url_for('properties.lotes_index', paquete_id=lote.paquete_id))
        
    return render_template('properties/lotes/form.html', 
                         form=form,
                         paquete=lote.paquete,
                         is_edit=True)

@bp.route('/properties/paquetes/<int:paquete_id>/lotes/bulk-upload', methods=['GET', 'POST'])
@login_required
@admin_required
def lotes_bulk_upload(paquete_id):
    paquete = Paquete.query.get_or_404(paquete_id)
    form = LoteBulkUploadForm()
    
    if form.validate_on_submit():
        try:
            # Read CSV file
            csv_file = form.file.data
            stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Validate headers
            required_headers = ['prototipo_id', 'calle', 'numero_exterior', 'manzana', 'lote', 'tipo_de_lote', 'estado_del_inmueble', 'precio']
            headers = csv_reader.fieldnames
            
            if not all(header in headers for header in required_headers):
                flash('El archivo CSV no tiene todas las columnas requeridas.', 'error')
                return redirect(url_for('properties.lotes_index', paquete_id=paquete_id))
            
            lotes_created = 0
            errors = []
            
            for row in csv_reader:
                try:
                    # Convert empty strings to None
                    for key in row:
                        if row[key] == '':
                            row[key] = None
                    
                    # Create new Lote
                    lote = Lote(
                        paquete_id=paquete_id,
                        prototipo_id=int(row['prototipo_id']),
                        calle=row['calle'],
                        numero_exterior=row['numero_exterior'],
                        numero_interior=row.get('numero_interior'),
                        manzana=row['manzana'],
                        lote=row['lote'],
                        cuv=row.get('cuv'),
                        terreno=float(row['terreno']) if row.get('terreno') else None,
                        tipo_de_lote=row['tipo_de_lote'],
                        estado_del_inmueble=row['estado_del_inmueble'],
                        precio=float(row['precio']),
                        orientacion_1=row.get('orientacion_1'),
                        medidas_orientacion_1=row.get('medidas_orientacion_1'),
                        colindancia_1=row.get('colindancia_1'),
                        orientacion_2=row.get('orientacion_2'),
                        medidas_orientacion_2=row.get('medidas_orientacion_2'),
                        colindancia_2=row.get('colindancia_2'),
                        orientacion_3=row.get('orientacion_3'),
                        medidas_orientacion_3=row.get('medidas_orientacion_3'),
                        colindancia_3=row.get('colindancia_3'),
                        orientacion_4=row.get('orientacion_4'),
                        medidas_orientacion_4=row.get('medidas_orientacion_4'),
                        colindancia_4=row.get('colindancia_4')
                    )
                    db.session.add(lote)
                    lotes_created += 1
                except Exception as e:
                    errors.append(f"Error en la fila {csv_reader.line_num}: {str(e)}")
            
            if errors:
                db.session.rollback()
                for error in errors:
                    flash(error, 'error')
            else:
                db.session.commit()
                flash(f'Se han creado {lotes_created} lotes exitosamente.', 'success')
            
            return redirect(url_for('properties.lotes_index', paquete_id=paquete_id))
            
        except Exception as e:
            flash(f'Error al procesar el archivo: {str(e)}', 'error')
            return redirect(url_for('properties.lotes_index', paquete_id=paquete_id))
    
    return render_template('properties/lotes/bulk_upload.html', 
                         form=form, 
                         paquete=paquete)

@bp.route('/api/lotes/<int:lote_id>/details', methods=['GET'])
@login_required
def get_lote_details(lote_id):
    """Get detailed information about a lot"""
    try:
        current_app.logger.info(f"Fetching details for lot {lote_id}")
        lote = Lote.query.get_or_404(lote_id)
        
        # Get current assignment if any
        current_assignment = None
        if lote.estado_del_inmueble == 'Apartado':
            current_assignment = (
                LoteAsignacion.query
                .filter_by(lote_id=lote_id, fecha_fin=None)
                .first()
            )
        
        # Build response data
        data = {
            'id': lote.id,
            'numero_lote': lote.lote,
            'manzana': lote.manzana,
            'superficie': lote.terreno,
            'precio': float(lote.precio) if lote.precio else 0,
            'estado': lote.estado_del_inmueble,
            'tipo': lote.tipo_de_lote,
            'prototipo': {
                'nombre': lote.prototipo.nombre_prototipo,
                'superficie': lote.prototipo.superficie_construccion
            } if lote.prototipo else None,
            'cliente': None
        }
        
        # Add client information if assigned
        if current_assignment and current_assignment.client:
            client = current_assignment.client
            data['cliente'] = {
                'nombre_completo': client.nombre_completo,
                'telefono': client.telefono,
                'email': client.email
            }
        
        current_app.logger.info(f"Successfully retrieved lot details: {data}")
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error getting lot details: {str(e)}")
        error_response = jsonify({'error': 'Error al obtener detalles del lote'})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@bp.route('/api/clients/assignable')
@login_required
def get_assignable_clients():
    """Get list of clients that can be assigned lots by the current user"""
    try:
        current_app.logger.info("Loading assignable clients")
        clients = current_user.get_assignable_clients()
        return jsonify([{
            'id': client.id,
            'nombre_completo': client.nombre_completo,
            'celular': client.celular or 'Sin teléfono'
        } for client in clients])
    except Exception as e:
        current_app.logger.error(f"Error in get_assignable_clients: {str(e)}")
        return jsonify({'error': 'Error al cargar la lista de clientes'}), 500

@bp.route('/api/lotes/<int:lote_id>/assign', methods=['POST'])
@login_required
def assign_lot(lote_id):
    """Assign a lot to a client"""
    try:
        current_app.logger.info(f"Starting lot assignment for lote_id: {lote_id}")
        data = request.get_json()
        current_app.logger.debug(f"Received data: {data}")
        
        client_id = data.get('client_id')
        notas = data.get('notas', '')

        if not client_id:
            current_app.logger.warning("No client_id provided in request")
            return jsonify({'error': 'Se requiere un cliente'}), 400

        # Get the lot and verify it exists
        lote = Lote.query.get_or_404(lote_id)
        current_app.logger.info(f"Found lot: {lote.id}, current status: {lote.estado_del_inmueble}")

        # Verify lot is available
        if lote.estado_del_inmueble != 'Libre':
            current_app.logger.warning(f"Lot {lote_id} is not available. Current status: {lote.estado_del_inmueble}")
            return jsonify({'error': 'El lote no está disponible'}), 400

        # Get the client and verify they exist
        client = Client.query.get_or_404(client_id)
        current_app.logger.info(f"Found client: {client.id}")

        try:
            # Start database transaction
            db.session.begin_nested()

            # Create new assignment using only the existing columns
            assignment = LoteAsignacion(
                lote_id=lote_id,
                client_id=client_id,
                user_id=current_user.id,
                notas=notas
            )
            current_app.logger.info(f"Created assignment object for lot {lote_id} and client {client_id}")

            # Update lot status
            lote.estado_del_inmueble = 'Apartado'
            current_app.logger.info(f"Updated lot status to Apartado")

            # Save changes
            db.session.add(assignment)
            db.session.commit()
            current_app.logger.info(f"Successfully saved assignment to database")

            return jsonify({
                'message': 'Lote apartado exitosamente',
                'lote_id': lote_id,
                'client_id': client_id,
                'estado': 'Apartado'
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during assignment: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'error': f'Error en la base de datos: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Error in assign_lot: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Error al apartar el lote: {str(e)}'}), 500

@bp.route('/api/lotes/<int:lote_id>/history')
@login_required
def get_lot_history(lote_id):
    """Get assignment history for a lot"""
    lote = Lote.query.get_or_404(lote_id)
    
    # Check if user can view this lot
    if not current_user.has_role(UserRole.ADMIN) and not current_user.has_role(UserRole.GERENTE):
        # Add any additional access control if needed
        pass
    
    # Get all historical records
    history = LoteAsignacionHistorial.query.filter_by(lote_id=lote_id)\
        .order_by(LoteAsignacionHistorial.fecha_inicio.desc()).all()
    
    return jsonify([{
        'fecha_inicio': record.fecha_inicio.isoformat(),
        'fecha_fin': record.fecha_fin.isoformat(),
        'client_name': f"{record.client.nombre} {record.client.apellido_paterno}",
        'estado': record.estado,
        'user_name': record.user.nombre_completo,
        'motivo_cambio': record.motivo_cambio
    } for record in history])

@bp.route('/api/lotes/<int:lote_id>/release', methods=['POST'])
@login_required
def release_lot(lote_id):
    """Release a lot back to available status"""
    data = request.get_json()
    
    if 'motivo' not in data:
        return jsonify({'error': 'Se requiere especificar el motivo'}), 400
    
    lote = Lote.query.get_or_404(lote_id)
    
    # Check if user can modify this assignment
    if not current_user.can_modify_lot_assignment(lote.asignacion):
        return jsonify({'error': 'No tiene permiso para liberar este lote'}), 403
    
    try:
        historial = lote.liberar_lote(
            user=current_user,
            motivo=data['motivo'],
            notas=data.get('notas')
        )
        
        db.session.add(historial)
        db.session.commit()
        
        return jsonify({
            'message': 'Lote liberado exitosamente',
            'lote_id': lote.id
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al liberar el lote'}), 500

@bp.route('/lotes/public', methods=['GET'])
def lotes_public():
    try:
        form = LoteFilterForm(request.args, meta={'csrf': False})
        lotes = []
        
        # If fraccionamiento_id is provided in AJAX request, return paquetes list
        if request.args.get('fraccionamiento_id'):
            fraccionamiento_id = int(request.args.get('fraccionamiento_id'))
            paquetes = Paquete.query.filter_by(fraccionamiento_id=fraccionamiento_id).order_by('nombre').all()
            return jsonify([(p.id, p.nombre) for p in paquetes])
        
        # Only build query if fraccionamiento is selected
        if form.fraccionamiento.data:
            # Update paquetes choices based on selected fraccionamiento
            paquetes = Paquete.query.filter_by(fraccionamiento_id=form.fraccionamiento.data).order_by('nombre').all()
            form.paquete.choices = [(0, 'Todos los paquetes')] + [(p.id, p.nombre) for p in paquetes]
            
            # Build query based on filters
            query = Lote.query
            paquete_ids = [p.id for p in paquetes]
            query = query.filter(Lote.paquete_id.in_(paquete_ids))
            
            if form.paquete.data and form.paquete.data != 0:  # 0 means "All packages"
                query = query.filter_by(paquete_id=form.paquete.data)
            
            if form.estado.data:
                query = query.filter_by(estado_del_inmueble=form.estado.data)
            
            # Get lotes with their relationships
            lotes = query.join(Paquete).join(Fraccionamiento).join(Prototipo).order_by(
                Fraccionamiento.nombre,
                Paquete.nombre,
                Lote.manzana,
                Lote.lote
            ).all()
        
        return render_template('properties/lotes/public.html', form=form, lotes=lotes)
    except Exception as e:
        current_app.logger.error(f"Error in lotes_public: {str(e)}")
        flash('Error al cargar los lotes. Por favor intente nuevamente.', 'error')
        return render_template('properties/lotes/public.html', form=form, lotes=[])
