"""remove duplicate telefono field

Revision ID: bd10f42038a7
Revises: 8ae16d2ba3c2
Create Date: 2024-11-26 20:21:38.308008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd10f42038a7'
down_revision = '8ae16d2ba3c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('telefono_empresa')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telefono_empresa', sa.VARCHAR(length=20), nullable=True))

    # ### end Alembic commands ###
