"""add avatar ao usuario

Revision ID: b3f2c9a1d4e7
Revises: ef70ca68a7a1
Create Date: 2026-07-31 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f2c9a1d4e7'
down_revision: Union[str, None] = 'ef70ca68a7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('avatar', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('usuarios', 'avatar')
