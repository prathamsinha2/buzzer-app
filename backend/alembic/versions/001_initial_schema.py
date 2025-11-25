"""Initial schema - create all tables

Revision ID: 001
Revises:
Create Date: 2024-11-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('invite_code', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invite_code'),
    )
    op.create_index('ix_groups_invite_code', 'groups', ['invite_code'])

    # Create group_members table
    op.create_table(
        'group_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(255), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('device_type', sa.String(100), nullable=True),
        sa.Column('browser_info', sa.JSON(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id'),
    )
    op.create_index('ix_devices_device_id', 'devices', ['device_id'])
    op.create_index('ix_devices_is_online', 'devices', ['is_online'])

    # Create ring_sessions table
    op.create_table(
        'ring_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('initiated_by', sa.Integer(), nullable=False),
        sa.Column('target_device_id', sa.Integer(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['target_device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ring_sessions_target_device_id', 'ring_sessions', ['target_device_id'])
    op.create_index('ix_ring_sessions_status', 'ring_sessions', ['status'])


def downgrade() -> None:
    op.drop_index('ix_ring_sessions_status', table_name='ring_sessions')
    op.drop_index('ix_ring_sessions_target_device_id', table_name='ring_sessions')
    op.drop_table('ring_sessions')
    op.drop_index('ix_devices_is_online', table_name='devices')
    op.drop_index('ix_devices_device_id', table_name='devices')
    op.drop_table('devices')
    op.drop_table('group_members')
    op.drop_index('ix_groups_invite_code', table_name='groups')
    op.drop_table('groups')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
