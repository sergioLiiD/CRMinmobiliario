"""Add fecha_modificacion to Lote

Revision ID: 3561395c1d25
Revises: 0e640ad535a9
Create Date: 2024-12-02 22:08:57.245634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3561395c1d25'
down_revision = '0e640ad535a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_modificacion', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.drop_column('fecha_modificacion')

    # ### end Alembic commands ###