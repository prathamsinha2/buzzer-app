"""Add push_subscription to devices

Revision ID: add_push_sub
Revises: 
Create Date: 2023-11-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_push_sub'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column exists first to avoid errors if run multiple times
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('devices')]
    
    if 'push_subscription' not in columns:
        op.add_column('devices', sa.Column('push_subscription', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('devices', 'push_subscription')
