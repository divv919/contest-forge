from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from sqlalchemy import DateTime
from sqlmodel import Column, Field, Relationship, SQLModel, Text

if TYPE_CHECKING:
    from .contests import Contest, ContestSubmission
    from .language import Language
    from .problem import Problem
    from .user import User


class SubmissionStatusId(int, Enum):
    IN_QUEUE = 1
    PROCESSING = 2
    AC = 3
    WA = 4
    TLE = 5
    CE = 6
    RTE_SIGSEGV = 7
    RTE_SIGXFSZ = 8
    RTE_SIGFPE = 9
    RTE_SIGABRT = 10
    NZEC = 11
    RTE_OTHER = 12
    INTERNAL_ERROR = 13
    EXEC_FORMAT_ERROR = 14


class SubmissionStatus(BaseModel):
    id: SubmissionStatusId
    description: str | None = None


class SubmissionBase(SQLModel, table=False):
    stdout: str | None = None
    time: str | None = None
    memory: int | None = None
    stderr: str | None = None
    token: str
    compile_output: str | None = None
    status: SubmissionStatusId


class SubmissionAPI(SubmissionBase):
    status: SubmissionStatus


class TestCase(SubmissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submission.id", ondelete="CASCADE")
    submission: "Submission" = Relationship(back_populates="test_cases")
    stdin: str | None
    expected_output: str | None


class Submission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_code: str | None = Field(sa_column=Column(Text, nullable=False))
    problem_id: int = Field(foreign_key="problem.id", ondelete="CASCADE")
    active_contest_id: int | None = Field(
        default=None, foreign_key="contest.id", ondelete="CASCADE"
    )
    language_id: int = Field(foreign_key="language.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    status: SubmissionStatusId
    total_testcases: int = Field(default=0)
    total_passed_cases: int = Field(default=0)
    max_memory: int | None = Field(default=None)
    total_time: str | None = Field(default=None)
    problem: "Problem" = Relationship(back_populates="submissions")
    active_contest: "Contest" = Relationship(back_populates="submissions")
    language: "Language" = Relationship(back_populates="submissions")
    user: "User" = Relationship(back_populates="submissions")
    test_cases: list["TestCase"] = Relationship(back_populates="submission")
    contests_submissions_link: list["ContestSubmission"] = Relationship(back_populates="submission")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class SubmissionRequest(BaseModel):
    problem_id: int
    source_code: str
    language_id: int
    active_contest_id: int | None = None


class SubmissionResponse(BaseModel):
    submission_id: int
    message: str
    total_test_cases: int


class Judge0RequestObject(BaseModel):
    source_code: str
    stdin: str
    expected_output: str
    language_id: int
    callback_url: str


class Judge0SubmitResponseObject(BaseModel):
    token: str


class SubmissionStatusBase(BaseModel):
    total_testcases: int | None = None
    total_passed_cases: int | None = None
    max_memory: int | None = None
    total_time: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    compile_output: str | None = None
    status: SubmissionStatusId | None = None
    message: str | None = None
    is_truncated_for_contest: bool = False


class SubmissionStatusResponse(SubmissionStatusBase):
    state: Literal["PENDING", "FINISH"]


class SubmissionsPaginatedRequest(BaseModel):
    current_page: int
    problem_id: int


class UserSubmissionsRequest(BaseModel):
    current_page: int


class SubmissionsPaginatedResponse(BaseModel):
    id: int | None = None
    problem_id: int | None = None
    active_contest_id: int | None = None
    status: SubmissionStatusId
    language: str
    max_memory: int | None = None
    total_time: str | None = None
    created_at: datetime | None = None


class ContestSubmissionsResponse(BaseModel):
    id: int
    problem_id: int
    active_contest_id: int
    language_id: int
    status: SubmissionStatusId
    total_testcases: int | None = None
    total_passed_cases: int | None = None
    max_memory: int | None = None
    total_time: str | None = None
    created_at: datetime
    points: int
