"""add document model

Revision ID: 3670bada5213
Revises: 8092a7ac2949
Create Date: 2024-11-26 21:12:32.142099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3670bada5213'
down_revision = '8092a7ac2949'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('filename', sa.String(length=200), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('document')
    # ### end Alembic commands ###