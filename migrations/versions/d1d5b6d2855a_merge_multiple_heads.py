"""merge multiple heads

Revision ID: d1d5b6d2855a
Revises: d4a7c2e3f9a1, 8e2b7cb3321c
Create Date: 2024-11-27 02:36:08.609019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1d5b6d2855a'
down_revision = ('d4a7c2e3f9a1', '8e2b7cb3321c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
