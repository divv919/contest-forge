"""Add slug column for contest

Revision ID: 2cb8101d2f1d
Revises: dbbcc9acaccf
Create Date: 2026-05-28 14:32:02.206794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cb8101d2f1d'
down_revision: Union[str, Sequence[str], None] = 'dbbcc9acaccf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("contest", sa.Column("slug",sa.String(),nullable=False))
    op.add_column("contest", sa.Column("is_finalized", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("contest", "slug")
    op.drop_column("contest", "is_finalized")
