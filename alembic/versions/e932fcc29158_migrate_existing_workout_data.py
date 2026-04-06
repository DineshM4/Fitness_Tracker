"""Migrate existing workout data

Revision ID: e932fcc29158
Revises: bae2630126bd
Create Date: 2026-04-06 10:54:15.672724

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlite3
import os


# revision identifiers, used by Alembic.
revision: str = 'e932fcc29158'
down_revision: Union[str, Sequence[str], None] = 'bae2630126bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - migrate existing data and update tables."""
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workout_logs.db')
    db_path = os.path.normpath(db_path)

    # Connect to existing SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if old table exists and has data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_logs'")
    old_table_exists = cursor.fetchone() is not None

    if old_table_exists:
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM workout_logs")
        row_count = cursor.fetchone()[0]

        if row_count > 0:
            # Get all existing data
            cursor.execute("SELECT id, exercise, sets, reps, weight, date FROM workout_logs")
            existing_workouts = cursor.fetchall()

            # Create a default user for existing data (user_id = 1)
            # Insert workouts with user_id = 1
            op.execute("""
                INSERT INTO workouts (id, user_id, exercise, sets, reps, weight, unit, date)
                SELECT id, 1, exercise, sets, reps, weight, 'kg', date
                FROM workout_logs
            """)

            # Update sequence for new workouts table
            op.execute("SELECT setval('workouts_id_seq', (SELECT MAX(id) FROM workouts))")

    conn.close()


def downgrade() -> None:
    """Downgrade schema."""
    # Note: Data migration cannot be automatically reversed safely
    # Manual cleanup may be required
    pass
