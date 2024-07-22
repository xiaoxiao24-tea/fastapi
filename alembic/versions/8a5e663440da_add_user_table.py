"""add user table

Revision ID: 8a5e663440da
Revises: 79edef593da5
Create Date: 2024-07-14 14:23:23.756434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a5e663440da'
down_revision: Union[str, None] = '79edef593da5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table( 'users',
                    sa.Column('id', sa.Integer(), nullable= False),
                    sa.Column('email', sa.String(), nullable= False),
                    sa.Column('password', sa.String(), nullable= False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone= False), server_default=sa.text('now()'), nullable= False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
    )
    
    
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
