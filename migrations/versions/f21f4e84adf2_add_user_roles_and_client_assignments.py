"""add user roles and client assignments

Revision ID: f21f4e84adf2
Revises: e5a8c2f4d9b2
Create Date: 2024-11-26 22:32:37.685217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f21f4e84adf2'
down_revision = 'e5a8c2f4d9b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Skip team_leader_assignments table as it already exists
    
    # Add new columns to user table first
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Add columns with nullable=True first
        batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
    
    # Set default role for existing users
    op.execute("UPDATE user SET role = 'VENDEDOR' WHERE role IS NULL")
    
    # Now make role not nullable
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role', nullable=False)
        batch_op.drop_column('is_admin')

    # Add new columns to client table
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default assigned_user_id for existing clients
    op.execute("""
        UPDATE client 
        SET assigned_user_id = (SELECT id FROM user LIMIT 1)
        WHERE assigned_user_id IS NULL
    """)
    
    # Now make assigned_user_id not nullable and add foreign key
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('assigned_user_id', nullable=False)
        batch_op.create_foreign_key(
            'fk_client_assigned_user',
            'user',
            ['assigned_user_id'],
            ['id']
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('last_login')
        batch_op.drop_column('created_at')
        batch_op.drop_column('role')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_constraint('fk_client_assigned_user', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('assigned_user_id')

    # Skip dropping team_leader_assignments table as we didn't create it
    # ### end Alembic commands ###
