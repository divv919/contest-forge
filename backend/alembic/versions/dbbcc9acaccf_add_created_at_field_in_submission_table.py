"""Add created_at field in submission table

Revision ID: dbbcc9acaccf
Revises: 0ff4128c0d48
Create Date: 2026-05-27 11:24:35.762115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbbcc9acaccf'
down_revision: Union[str, Sequence[str], None] = '0ff4128c0d48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "submission",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("submission", "created_at")
