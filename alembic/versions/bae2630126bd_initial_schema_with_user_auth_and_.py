"""Initial schema with user auth and extended workout

Revision ID: bae2630126bd
Revises:
Create Date: 2026-04-06 10:53:46.441517

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bae2630126bd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create workouts table with extended schema
    op.create_table('workouts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('exercise', sa.String(length=100), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=10), default='kg'),
        sa.Column('rpe', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create exercise presets table
    op.create_table('exercise_presets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sets', sa.Integer(), default=3),
        sa.Column('reps', sa.String(length=50), default='8-12'),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_workouts_exercise', 'workouts', ['exercise'], unique=False)
    op.create_index('ix_workouts_date', 'workouts', ['date'], unique=False)
    op.create_index('ix_workouts_user_id', 'workouts', ['user_id'], unique=False)
    op.create_index('ix_exercise_presets_user_id', 'exercise_presets', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_exercise_presets_user_id', table_name='exercise_presets')
    op.drop_index('ix_workouts_user_id', table_name='workouts')
    op.drop_index('ix_workouts_date', table_name='workouts')
    op.drop_index('ix_workouts_exercise', table_name='workouts')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('exercise_presets')
    op.drop_table('workouts')
    op.drop_table('users')
