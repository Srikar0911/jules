from sqlalchemy import MetaData, Table, Column, DateTime, inspect

meta = MetaData()

def upgrade(op):
    inspector = inspect(op.get_bind())
    if 'due_date' not in [c['name'] for c in inspector.get_columns('tasks')]:
        op.add_column('tasks', Column('due_date', DateTime, nullable=True))


def downgrade(op):
    inspector = inspect(op.get_bind())
    if 'due_date' in [c['name'] for c in inspector.get_columns('tasks')]:
        op.drop_column('tasks', 'due_date')
