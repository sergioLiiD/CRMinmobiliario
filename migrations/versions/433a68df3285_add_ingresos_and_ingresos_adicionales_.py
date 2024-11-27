"""Add ingresos and ingresos_adicionales columns to client

Revision ID: 433a68df3285
Revises: a7de7fd3fd22
Create Date: 2024-11-27 18:14:52.892392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '433a68df3285'
down_revision = 'a7de7fd3fd22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ingresos', sa.Float(), nullable=True))
        batch_op.alter_column('ingresos_adicionales',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('estatus',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               nullable=False)
        batch_op.drop_column('ingreso_mensual')
        batch_op.drop_column('horario')
        batch_op.drop_column('extension')
        batch_op.drop_column('empresa_estado')
        batch_op.drop_column('empresa_colonia')
        batch_op.drop_column('url')
        batch_op.drop_column('telefono')
        batch_op.drop_column('empresa_codigo_postal')

    with op.batch_alter_table('lote_asignaciones', schema=None) as batch_op:
        batch_op.alter_column('fecha_asignacion',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lote_asignaciones', schema=None) as batch_op:
        batch_op.alter_column('fecha_asignacion',
               existing_type=sa.DATETIME(),
               nullable=False)

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('empresa_codigo_postal', sa.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('telefono', sa.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('url', sa.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('empresa_colonia', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('empresa_estado', sa.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('extension', sa.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('horario', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('ingreso_mensual', sa.NUMERIC(precision=10, scale=2), nullable=True))
        batch_op.alter_column('estatus',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('ingresos_adicionales',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
        batch_op.drop_column('ingresos')

    # ### end Alembic commands ###