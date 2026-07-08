"""crear tablas user y household

Revision ID: b81625a3ea32
Revises: 
Create Date: 2026-07-08 01:53:45.916046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b81625a3ea32'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.create_table('household',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('invite_code', sa.String(length=20), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('owner_id')
    )
    op.create_index(op.f('ix_household_invite_code'), 'household', ['invite_code'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('role', sa.Enum('PADRE', 'HIJO', name='user_role'), nullable=False),
    sa.Column('household_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['household_id'], ['household.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # Ahora que ambas tablas existen, se añade la FK circular restante
    op.create_foreign_key(
        'fk_household_owner_id', 'household', 'users', ['owner_id'], ['id']
    )
    # ### end Alembic commands ###



def downgrade() -> None:

    op.drop_constraint('fk_household_owner_id', 'household', type_='foreignkey')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_household_invite_code'), table_name='household')
    op.drop_table('household')
    # ### end Alembic commands ###