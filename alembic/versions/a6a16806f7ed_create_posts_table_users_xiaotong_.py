"""create posts table/Users/xiaotong/fastapi/venv/bin/python

Revision ID: a6a16806f7ed
Revises: 62d514b60058
Create Date: 2024-07-14 14:45:49.510232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6a16806f7ed'
down_revision: Union[str, None] = '62d514b60058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
