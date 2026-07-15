"""cambiar hashed_password por firebase_id

Revision ID: b25cfd816d78
Revises: 48573461ccfb
Create Date: 2026-07-08 23:50:03.035007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b25cfd816d78'
down_revision: Union[str, Sequence[str], None] = '48573461ccfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('firebase_id', sa.String(length=128), nullable=False))
    op.create_index(op.f('ix_users_firebase_id'), 'users', ['firebase_id'], unique=True)
    op.drop_column('users', 'hashed_password')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_firebase_id'), table_name='users')
    op.drop_column('users', 'firebase_id')