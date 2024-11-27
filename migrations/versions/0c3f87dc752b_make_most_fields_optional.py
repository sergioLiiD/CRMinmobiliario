"""make most fields optional

Revision ID: 0c3f87dc752b
Revises: 3670bada5213
Create Date: 2024-11-26 21:22:12.452999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c3f87dc752b'
down_revision = '3670bada5213'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('sexo',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('estado_civil',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('regimen_matrimonial',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
        batch_op.alter_column('celular',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('tipo_de_credito',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('colonia',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('como_se_entero',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('rfc_empresa',
               existing_type=sa.VARCHAR(length=13),
               nullable=True)
        batch_op.alter_column('nrp',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('telefono',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('extension',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('horario',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('ingresos_adicionales',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('empresa_colonia',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('empresa_estado',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('empresa_codigo_postal',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('ref1_nombre',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('apellido_paterno_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('apellido_materno_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('telefono_celular_referencia_1',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('direccion_referencia_1',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('estado_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('colonia_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('entidad_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('municipio_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('codigo_postal_referencia_1',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('ref2_nombre',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('apellido_paterno_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('apellido_materno_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('telefono_celular_referencia_2',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('direccion_referencia_2',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.alter_column('estado_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('colonia_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('entidad_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('municipio_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('codigo_postal_referencia_2',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('codigo_postal_referencia_2',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('municipio_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('entidad_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('colonia_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('estado_referencia_2',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('direccion_referencia_2',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('telefono_celular_referencia_2',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('apellido_materno_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('apellido_paterno_referencia_2',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('ref2_nombre',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('codigo_postal_referencia_1',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('municipio_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('entidad_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('colonia_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('estado_referencia_1',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('direccion_referencia_1',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('telefono_celular_referencia_1',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('apellido_materno_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('apellido_paterno_referencia_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('ref1_nombre',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('empresa_codigo_postal',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('empresa_estado',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('empresa_colonia',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('ingresos_adicionales',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('horario',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('extension',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('telefono',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('nrp',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('rfc_empresa',
               existing_type=sa.VARCHAR(length=13),
               nullable=False)
        batch_op.alter_column('como_se_entero',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('colonia',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('tipo_de_credito',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('celular',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
        batch_op.alter_column('regimen_matrimonial',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('estado_civil',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('sexo',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)

    # ### end Alembic commands ###