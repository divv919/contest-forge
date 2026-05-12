from enum import Enum
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, Text


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
    id : SubmissionStatusId
    description: str | None = None

class SubmissionBase(SQLModel, table=False):
    stdout : str | None = None
    time: str 
    memory : int
    stderr: str | None = None
    token: str
    compile_output: str | None = None
    status : SubmissionStatusId

class SubmissionAPI(SubmissionBase):
    status: SubmissionStatus

class TestCase(SubmissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id : int = Field(foreign_key="submission.id", ondelete="CASCADE")


class SubmissionInDB(SubmissionBase, table=True):
    id: str | None = Field(default=None, primary_key=True)
    source_code: str | None = Field(sa_column=Column(Text, nullable=False))
    problem_id: int = Field(foreign_key="problem.id", ondelete="CASCADE")
    active_contest_id: int | None = Field(foreign_key="contest.id", ondelete="CASCADE")
    language_id: int = Field(foreign_key="language.id",ondelete="CASCADE")
    user_id : int = Field(foreign_key="user.id", ondelete="CASCADE")
    status: SubmissionStatusId
    total_testcases: int = Field(default=0) 
    total_passed_cases : int = Field(default=0)
    max_memory: int | None = Field(default=None)
    total_time: int | None = Field(default=None)


