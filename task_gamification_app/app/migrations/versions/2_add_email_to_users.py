from sqlalchemy import MetaData, Table, Column, String, inspect

meta = MetaData()

def upgrade(op):
    inspector = inspect(op.get_bind())
    if 'email' not in [c['name'] for c in inspector.get_columns('users')]:
        op.add_column('users', Column('email', String, nullable=True))


def downgrade(op):
    inspector = inspect(op.get_bind())
    if 'email' in [c['name'] for c in inspector.get_columns('users')]:
        op.drop_column('users', 'email')
