"""Add first_name and last_name to users

Revision ID: 3
Revises: 2
Create Date: 2024-05-16 10:00:00.000000

"""
from alembic.operations import Operations
from sqlalchemy import Column, String

# revision identifiers, used by this migration.
revision = '3'
down_revision = '2'
branch_labels = None
depends_on = None


from sqlalchemy import inspect

def upgrade(op: Operations):
    inspector = inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'first_name' not in columns:
        op.add_column('users', Column('first_name', String(length=50), nullable=True))
    if 'last_name' not in columns:
        op.add_column('users', Column('last_name', String(length=50), nullable=True))


def downgrade(op: Operations):
    inspector = inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'first_name' in columns:
        op.drop_column('users', 'first_name')
    if 'last_name' in columns:
        op.drop_column('users', 'last_name')
