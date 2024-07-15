"""add content column to posts table

Revision ID: 79edef593da5
Revises: 09dba5240276
Create Date: 2024-07-14 14:18:53.483592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79edef593da5'
down_revision: Union[str, None] = '09dba5240276'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable =False))
    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
