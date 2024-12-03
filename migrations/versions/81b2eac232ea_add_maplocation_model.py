"""Add MapLocation model

Revision ID: 81b2eac232ea
Revises: 3561395c1d25
Create Date: 2024-12-03 02:00:33.790500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81b2eac232ea'
down_revision = '3561395c1d25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('map_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lot_id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['lot_id'], ['lotes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('map_locations')
    # ### end Alembic commands ###