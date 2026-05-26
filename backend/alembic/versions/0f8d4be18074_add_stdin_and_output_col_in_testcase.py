"""add stdin and output col in testcase

Revision ID: 0f8d4be18074
Revises: 9c594c936706
Create Date: 2026-05-26 18:43:15.941250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f8d4be18074'
down_revision: Union[str, Sequence[str], None] = '9c594c936706'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("testcase", sa.Column("stdin", sa.String(), nullable=True))
    op.add_column("testcase", sa.Column("expected_output", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("testcase", "stdin")
    op.drop_column("testcase", "expected_output")
