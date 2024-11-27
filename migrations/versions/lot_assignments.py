"""lot assignments

Revision ID: lot_assignments
Revises: 
Create Date: 2024-01-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'lot_assignments'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create lote_asignaciones table
    op.create_table('lote_asignaciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lote_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
        sa.ForeignKeyConstraint(['lote_id'], ['lotes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create lote_asignaciones_historial table
    op.create_table('lote_asignaciones_historial',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lote_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False),
        sa.Column('motivo_cambio', sa.String(length=100), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
        sa.ForeignKeyConstraint(['lote_id'], ['lotes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('lote_asignaciones_historial')
    op.drop_table('lote_asignaciones')
