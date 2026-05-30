"""Add user_id column in contest submissions

Revision ID: d1c662bc5cf9
Revises: 2cb8101d2f1d
Create Date: 2026-05-30 12:39:34.227261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1c662bc5cf9'
down_revision: Union[str, Sequence[str], None] = '2cb8101d2f1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("contestsubmission", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "fk_contestsubmission_user_id_user",
        "contestsubmission",
        "user",
        ["user_id"],
        ["id"],)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("contestsubmission", "user_id")
    op.drop_constraint("fk_contestsubmission_user_id_user", "contestsubmission", type_="foreignkey")
