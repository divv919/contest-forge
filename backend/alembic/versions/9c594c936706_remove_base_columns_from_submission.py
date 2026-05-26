"""remove base columns from submission

Revision ID: 9c594c936706
Revises: b87b6ad50bc9
Create Date: 2026-05-26 12:32:02.770341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c594c936706'
down_revision: Union[str, Sequence[str], None] = 'b87b6ad50bc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("submission", "stdout")
    op.drop_column("submission", "token")
    op.drop_column("submission", "compile_output")
    op.drop_column("submission", "stderr")
    op.drop_column("submission", "memory")
    op.drop_column("submission", "time")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("submission",sa.Column("stdout", sa.String(), nullable=True))
    op.add_column("submission",sa.Column("token", sa.String(), nullable=False))
    op.add_column("submission",sa.Column("compile_output", sa.String(), nullable=True))
    op.add_column("submission",sa.Column("stderr", sa.String(), nullable=True))
    op.add_column("submission",sa.Column("memory", sa.String(), nullable=False))
    op.add_column("submission",sa.Column("time", sa.String(), nullable=False))

