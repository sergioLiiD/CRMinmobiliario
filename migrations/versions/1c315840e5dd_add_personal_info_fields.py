"""add_personal_info_fields

Revision ID: 1c315840e5dd
Revises: cc2aa163e2ff
Create Date: 2024-11-26 18:08:23.991323

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '1c315840e5dd'
down_revision = 'cc2aa163e2ff'
branch_labels = None
depends_on = None


def upgrade():
    # Create new table
    op.create_table('client_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.String(length=200), nullable=True),
        sa.Column('ciudad', sa.String(length=64), nullable=True),
        sa.Column('estado', sa.String(length=64), nullable=True),
        sa.Column('codigo_postal', sa.String(length=10), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('ultima_contacto', sa.DateTime(), nullable=True),
        sa.Column('estatus', sa.String(length=20), nullable=True),
        sa.Column('tipo_propiedad', sa.String(length=50), nullable=True),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=False),
        sa.Column('nacionalidad', sa.String(length=50), nullable=True),
        sa.Column('estado_civil', sa.String(length=20), nullable=False),
        sa.Column('rfc', sa.String(length=13), nullable=True),
        sa.Column('curp', sa.String(length=18), nullable=True),
        sa.Column('nombre_empresa', sa.String(length=100), nullable=True),
        sa.Column('puesto', sa.String(length=100), nullable=True),
        sa.Column('antiguedad', sa.Integer(), nullable=True),
        sa.Column('ingreso_mensual', sa.Float(), nullable=True),
        sa.Column('direccion_empresa', sa.String(length=200), nullable=True),
        sa.Column('telefono_empresa', sa.String(length=20), nullable=True),
        sa.Column('email_empresa', sa.String(length=120), nullable=True),
        sa.Column('sector', sa.String(length=50), nullable=True),
        sa.Column('ref1_nombre', sa.String(length=200), nullable=True),
        sa.Column('ref1_telefono', sa.String(length=20), nullable=True),
        sa.Column('ref1_relacion', sa.String(length=50), nullable=True),
        sa.Column('ref2_nombre', sa.String(length=200), nullable=True),
        sa.Column('ref2_telefono', sa.String(length=20), nullable=True),
        sa.Column('ref2_relacion', sa.String(length=50), nullable=True),
        sa.Column('conyuge_nombre', sa.String(length=64), nullable=True),
        sa.Column('conyuge_apellido_paterno', sa.String(length=64), nullable=True),
        sa.Column('conyuge_apellido_materno', sa.String(length=64), nullable=True),
        sa.Column('conyuge_fecha_nacimiento', sa.Date(), nullable=True),
        sa.Column('conyuge_rfc', sa.String(length=13), nullable=True),
        sa.Column('conyuge_curp', sa.String(length=18), nullable=True),
        sa.Column('conyuge_email', sa.String(length=120), nullable=True),
        sa.Column('conyuge_telefono', sa.String(length=20), nullable=True),
        sa.Column('conyuge_celular', sa.String(length=20), nullable=True),
        sa.Column('conyuge_nombre_empresa', sa.String(length=100), nullable=True),
        sa.Column('conyuge_puesto', sa.String(length=100), nullable=True),
        sa.Column('conyuge_antiguedad', sa.Integer(), nullable=True),
        sa.Column('conyuge_ingreso_mensual', sa.Float(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('sexo', sa.String(length=20), nullable=False),
        sa.Column('regimen_matrimonial', sa.String(length=50), nullable=False),
        sa.Column('colonia', sa.String(length=100), nullable=False),
        sa.Column('como_se_entero', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Copy data from old table to new table
    op.execute("""
        INSERT INTO client_new 
        SELECT 
            id, nombre, email, telefono, celular, direccion, ciudad, estado, 
            codigo_postal, fecha_registro, notas, ultima_contacto, estatus, 
            tipo_propiedad, 
            COALESCE(fecha_nacimiento, '2000-01-01') as fecha_nacimiento,
            nacionalidad,
            COALESCE(estado_civil, 'soltero') as estado_civil,
            rfc, curp, nombre_empresa, puesto, antiguedad, ingreso_mensual,
            direccion_empresa, telefono_empresa, email_empresa, sector,
            ref1_nombre, ref1_telefono, ref1_relacion,
            ref2_nombre, ref2_telefono, ref2_relacion,
            conyuge_nombre, conyuge_apellido_paterno, conyuge_apellido_materno,
            conyuge_fecha_nacimiento, conyuge_rfc, conyuge_curp,
            conyuge_email, conyuge_telefono, conyuge_celular,
            conyuge_nombre_empresa, conyuge_puesto, conyuge_antiguedad,
            conyuge_ingreso_mensual, tipo,
            apellido_paterno || ' ' || apellido_materno as apellido,
            'masculino' as sexo,
            CASE 
                WHEN estado_civil = 'casado' THEN 'separacion_bienes'
                ELSE 'separacion_bienes'
            END as regimen_matrimonial,
            COALESCE(direccion, 'No especificada') as colonia,
            'otro' as como_se_entero
        FROM client
    """)

    # Drop old table and rename new table
    op.drop_table('client')
    op.rename_table('client_new', 'client')


def downgrade():
    # Create old table structure
    op.create_table('client_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido_paterno', sa.String(length=64), nullable=False),
        sa.Column('apellido_materno', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.String(length=200), nullable=True),
        sa.Column('ciudad', sa.String(length=64), nullable=True),
        sa.Column('estado', sa.String(length=64), nullable=True),
        sa.Column('codigo_postal', sa.String(length=10), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('ultima_contacto', sa.DateTime(), nullable=True),
        sa.Column('estatus', sa.String(length=20), nullable=True),
        sa.Column('tipo_propiedad', sa.String(length=50), nullable=True),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=True),
        sa.Column('lugar_nacimiento', sa.String(length=100), nullable=True),
        sa.Column('nacionalidad', sa.String(length=50), nullable=True),
        sa.Column('estado_civil', sa.String(length=20), nullable=True),
        sa.Column('rfc', sa.String(length=13), nullable=True),
        sa.Column('curp', sa.String(length=18), nullable=True),
        sa.Column('nombre_empresa', sa.String(length=100), nullable=True),
        sa.Column('puesto', sa.String(length=100), nullable=True),
        sa.Column('antiguedad', sa.Integer(), nullable=True),
        sa.Column('ingreso_mensual', sa.Float(), nullable=True),
        sa.Column('direccion_empresa', sa.String(length=200), nullable=True),
        sa.Column('telefono_empresa', sa.String(length=20), nullable=True),
        sa.Column('email_empresa', sa.String(length=120), nullable=True),
        sa.Column('sector', sa.String(length=50), nullable=True),
        sa.Column('ref1_nombre', sa.String(length=200), nullable=True),
        sa.Column('ref1_telefono', sa.String(length=20), nullable=True),
        sa.Column('ref1_relacion', sa.String(length=50), nullable=True),
        sa.Column('ref2_nombre', sa.String(length=200), nullable=True),
        sa.Column('ref2_telefono', sa.String(length=20), nullable=True),
        sa.Column('ref2_relacion', sa.String(length=50), nullable=True),
        sa.Column('conyuge_nombre', sa.String(length=64), nullable=True),
        sa.Column('conyuge_apellido_paterno', sa.String(length=64), nullable=True),
        sa.Column('conyuge_apellido_materno', sa.String(length=64), nullable=True),
        sa.Column('conyuge_fecha_nacimiento', sa.Date(), nullable=True),
        sa.Column('conyuge_rfc', sa.String(length=13), nullable=True),
        sa.Column('conyuge_curp', sa.String(length=18), nullable=True),
        sa.Column('conyuge_email', sa.String(length=120), nullable=True),
        sa.Column('conyuge_telefono', sa.String(length=20), nullable=True),
        sa.Column('conyuge_celular', sa.String(length=20), nullable=True),
        sa.Column('conyuge_nombre_empresa', sa.String(length=100), nullable=True),
        sa.Column('conyuge_puesto', sa.String(length=100), nullable=True),
        sa.Column('conyuge_antiguedad', sa.Integer(), nullable=True),
        sa.Column('conyuge_ingreso_mensual', sa.Float(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Copy data back
    op.execute("""
        INSERT INTO client_old
        SELECT 
            id, nombre, 
            apellido as apellido_paterno,
            '' as apellido_materno,
            email, telefono, celular, direccion, ciudad, estado,
            codigo_postal, fecha_registro, notas, ultima_contacto, estatus,
            tipo_propiedad, fecha_nacimiento,
            NULL as lugar_nacimiento,
            nacionalidad, estado_civil, rfc, curp,
            nombre_empresa, puesto, antiguedad, ingreso_mensual,
            direccion_empresa, telefono_empresa, email_empresa, sector,
            ref1_nombre, ref1_telefono, ref1_relacion,
            ref2_nombre, ref2_telefono, ref2_relacion,
            conyuge_nombre, conyuge_apellido_paterno, conyuge_apellido_materno,
            conyuge_fecha_nacimiento, conyuge_rfc, conyuge_curp,
            conyuge_email, conyuge_telefono, conyuge_celular,
            conyuge_nombre_empresa, conyuge_puesto, conyuge_antiguedad,
            conyuge_ingreso_mensual, tipo
        FROM client
    """)

    # Drop new table and rename old table back
    op.drop_table('client')
    op.rename_table('client_old', 'client')
