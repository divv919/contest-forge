"""change total time in submission to string

Revision ID: 0ff4128c0d48
Revises: 0f8d4be18074
Create Date: 2026-05-26 19:15:41.463272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ff4128c0d48'
down_revision: Union[str, Sequence[str], None] = '0f8d4be18074'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("submission", "total_time", type_=sa.String(), existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("submission", "total_time", type_=sa.String(), existing_type=sa.String(), nullable=True)
