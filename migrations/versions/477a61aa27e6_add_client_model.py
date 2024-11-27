"""Add client model

Revision ID: 477a61aa27e6
Revises: a0a7bae2b693
Create Date: 2024-11-26 13:56:59.961817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '477a61aa27e6'
down_revision = 'a0a7bae2b693'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=64), nullable=False),
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
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('presupuesto_min', sa.Float(), nullable=True),
    sa.Column('presupuesto_max', sa.Float(), nullable=True),
    sa.Column('zona_interes', sa.String(length=200), nullable=True),
    sa.Column('tipo_propiedad', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('client')
    # ### end Alembic commands ###
