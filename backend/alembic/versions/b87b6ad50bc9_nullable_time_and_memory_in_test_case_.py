"""nullable time and memory in test case model

Revision ID: b87b6ad50bc9
Revises: 236b68551a26
Create Date: 2026-05-26 11:28:24.904055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b87b6ad50bc9'
down_revision: Union[str, Sequence[str], None] = '236b68551a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("testcase", "memory", nullable=True)
    op.alter_column("testcase", "time", nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("testcase", "memory", nullable=False)
    op.alter_column("testcase", "time", nullable=False)
    