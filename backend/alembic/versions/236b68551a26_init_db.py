"""init db

Revision ID: 236b68551a26
Revises: 
Create Date: 2026-05-24 21:17:34.845405

"""
from typing import Any, Sequence, Union, cast

from alembic import context as alembic_context
import sqlalchemy as sa


context: Any = cast(Any, alembic_context)


metadata = sa.MetaData()


difficulty_enum = sa.Enum(
    "EASE",
    "MEDIUM",
    "HARD",
    name="difficulty",
)

submission_status_enum = sa.Enum(
    "IN_QUEUE",
    "PROCESSING",
    "AC",
    "WA",
    "TLE",
    "CE",
    "RTE_SIGSEGV",
    "RTE_SIGXFSZ",
    "RTE_SIGFPE",
    "RTE_SIGABRT",
    "NZEC",
    "RTE_OTHER",
    "INTERNAL_ERROR",
    "EXEC_FORMAT_ERROR",
    name="submissionstatusid",
)


user_table = sa.Table(
    "user",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("username", sa.String(), nullable=False),
    sa.Column("provider", sa.String(), nullable=False),
    sa.Column("provider_user_id", sa.String(), nullable=False),
    sa.Column("email", sa.String(), nullable=True),
    sa.Column("password", sa.String(), nullable=False),
)

language_table = sa.Table(
    "language",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("judge0id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
)

problem_table = sa.Table(
    "problem",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),
    sa.Column("solution", sa.Text(), nullable=False),
    sa.Column("slug", sa.String(), nullable=False),
    sa.Column("test_cases_count", sa.Integer(), nullable=False),
    sa.Column("difficulty", difficulty_enum, nullable=False),
)

contest_table = sa.Table(
    "contest",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("startTime", sa.DateTime(timezone=True), nullable=False),
    sa.Column("endTime", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "created_by",
        sa.Integer(),
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

submission_table = sa.Table(
    "submission",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("stdout", sa.String(), nullable=True),
    sa.Column("time", sa.String(), nullable=False),
    sa.Column("memory", sa.Integer(), nullable=False),
    sa.Column("stderr", sa.String(), nullable=True),
    sa.Column("token", sa.String(), nullable=False),
    sa.Column("compile_output", sa.String(), nullable=True),
    sa.Column("status", submission_status_enum, nullable=False),
    sa.Column("source_code", sa.Text(), nullable=False),
    sa.Column(
        "problem_id",
        sa.Integer(),
        sa.ForeignKey("problem.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "active_contest_id",
        sa.Integer(),
        sa.ForeignKey("contest.id", ondelete="CASCADE"),
        nullable=True,
    ),
    sa.Column(
        "language_id",
        sa.Integer(),
        sa.ForeignKey("language.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "user_id",
        sa.Integer(),
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("total_testcases", sa.Integer(), nullable=False),
    sa.Column("total_passed_cases", sa.Integer(), nullable=False),
    sa.Column("max_memory", sa.Integer(), nullable=True),
    sa.Column("total_time", sa.Integer(), nullable=True),
)

testcase_table = sa.Table(
    "testcase",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column("stdout", sa.String(), nullable=True),
    sa.Column("time", sa.String(), nullable=False),
    sa.Column("memory", sa.Integer(), nullable=False),
    sa.Column("stderr", sa.String(), nullable=True),
    sa.Column("token", sa.String(), nullable=False),
    sa.Column("compile_output", sa.String(), nullable=True),
    sa.Column("status", submission_status_enum, nullable=False),
    sa.Column(
        "submission_id",
        sa.Integer(),
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

contest_points_table = sa.Table(
    "contest_points",
    metadata,
    sa.Column("total_points", sa.Integer(), nullable=False),
    sa.Column("rank", sa.Integer(), nullable=False),
    sa.Column(
        "user_id",
        sa.Integer(),
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "contest_id",
        sa.Integer(),
        sa.ForeignKey("contest.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)

contestproblems_table = sa.Table(
    "contestproblems",
    metadata,
    sa.Column("solve_count", sa.Integer(), nullable=False),
    sa.Column(
        "problem_id",
        sa.Integer(),
        sa.ForeignKey("problem.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "contest_id",
        sa.Integer(),
        sa.ForeignKey("contest.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)

contestsubmission_table = sa.Table(
    "contestsubmission",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    sa.Column(
        "submission_id",
        sa.Integer(),
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "contest_id",
        sa.Integer(),
        sa.ForeignKey("contest.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "problem_id",
        sa.Integer(),
        sa.ForeignKey("problem.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("points", sa.Integer(), nullable=False),
)

boilerplate_table = sa.Table(
    "boilerplate",
    metadata,
    sa.Column(
        "problem_id",
        sa.Integer(),
        sa.ForeignKey("problem.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "language_id",
        sa.Integer(),
        sa.ForeignKey("language.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column("boilerplate_code", sa.Text(), nullable=False),
)


def ensure_enum(bind: Any, enum_type: sa.Enum) -> None:
    exists = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = :type_name"),
        {"type_name": enum_type.name},
    ).first()
    if exists is None:
        enum_type.create(bind, checkfirst=False)


# revision identifiers, used by Alembic.
revision: str = '236b68551a26'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    bind = getattr(alembic_context, "get_context")().bind  # type: ignore[attr-defined]
    assert bind is not None

    # ensure_enum(bind, difficulty_enum)
    # ensure_enum(bind, submission_status_enum)

    user_table.create(bind, checkfirst=True)
    language_table.create(bind, checkfirst=True)
    problem_table.create(bind, checkfirst=True)
    contest_table.create(bind, checkfirst=True)
    submission_table.create(bind, checkfirst=True)
    testcase_table.create(bind, checkfirst=True)
    contest_points_table.create(bind, checkfirst=True)
    contestproblems_table.create(bind, checkfirst=True)
    contestsubmission_table.create(bind, checkfirst=True)
    boilerplate_table.create(bind, checkfirst=True)



def downgrade() -> None:
    """Downgrade schema."""
    bind = getattr(alembic_context, "get_context")().bind  # type: ignore[attr-defined]
    assert bind is not None

    boilerplate_table.drop(bind, checkfirst=True)
    contestsubmission_table.drop(bind, checkfirst=True)
    contestproblems_table.drop(bind, checkfirst=True)
    contest_points_table.drop(bind, checkfirst=True)
    testcase_table.drop(bind, checkfirst=True)
    submission_table.drop(bind, checkfirst=True)
    contest_table.drop(bind, checkfirst=True)
    problem_table.drop(bind, checkfirst=True)
    language_table.drop(bind, checkfirst=True)
    user_table.drop(bind, checkfirst=True)

    submission_status_enum.drop(bind, checkfirst=True)
    difficulty_enum.drop(bind, checkfirst=True)
