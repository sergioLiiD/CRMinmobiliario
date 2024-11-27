"""Add fecha_inicio and fecha_fin to lote_asignaciones

Revision ID: 56277d550ecb
Revises: 433a68df3285
Create Date: 2024-11-27 22:13:23.158482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56277d550ecb'
down_revision = '433a68df3285'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lote_asignaciones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_inicio', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('fecha_fin', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lote_asignaciones', schema=None) as batch_op:
        batch_op.drop_column('fecha_fin')
        batch_op.drop_column('fecha_inicio')

    # ### end Alembic commands ###
