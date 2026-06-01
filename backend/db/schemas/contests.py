
from datetime import datetime
from typing import ClassVar, TYPE_CHECKING
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
if TYPE_CHECKING:
    from .user import User
    from .submission import Submission
    from .problem import Problem
    from .problem import ContestInfoProblems
    
class Contest(SQLModel, table=True):
    id: int | None = Field(default=None , primary_key=True)
    name: str
    slug: str
    startTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    endTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    created_by: int = Field(foreign_key="user.id", ondelete="CASCADE")
    is_finalized: bool = Field(default=False)

    contest_points: list[ContestPoints] = Relationship(back_populates="contest")
    contests_problems_link: list[ContestProblems] = Relationship(back_populates="contest")
    contests_submissions_link: list[ContestSubmission] = Relationship(back_populates="contest")
    submissions: list["Submission"] = Relationship(back_populates="active_contest")

    user: "User" = Relationship(back_populates="contests")
    
class AllContestsResponse(BaseModel):
    id: int | None = None
    name: str
    slug: str
    startTime: datetime
    endTime: datetime
    created_by: str | None = None


class ContestPoints(SQLModel, table=True):
    __tablename__: ClassVar[str] = "contest_points"
    total_points: int
    rank: int
    user_id: int = Field(foreign_key="user.id" , ondelete="CASCADE", primary_key=True)
    contest_id: int = Field(foreign_key="contest.id", ondelete="CASCADE", primary_key=True)
    contest: Contest = Relationship(back_populates="contest_points")
    user: "User" = Relationship(back_populates="contest_points")


class ContestProblems(SQLModel, table=True):
    solve_count: int = Field(default=0)
    problem_id: int = Field(foreign_key="problem.id" , ondelete="CASCADE" , primary_key=True)
    contest_id: int = Field(foreign_key="contest.id", ondelete="CASCADE", primary_key=True)
    problem: "Problem" = Relationship(back_populates="contests_problems_link")
    contest: Contest = Relationship(back_populates="contests_problems_link")
    

    
class ContestSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submission.id", ondelete="CASCADE")
    contest_id : int = Field(foreign_key="contest.id", ondelete="CASCADE")
    problem_id : int = Field(foreign_key="problem.id", ondelete="CASCADE")
    user_id : int = Field(foreign_key="user.id", ondelete="CASCADE")
    points : int = Field(default=0)

    user: "User" = Relationship(back_populates="contests_submissions_link")
    problem: "Problem" = Relationship(back_populates="contests_submissions_link")
    contest: Contest = Relationship(back_populates="contests_submissions_link")
    submission: "Submission" = Relationship(back_populates="contests_submissions_link")


class ContestCreateRequest(BaseModel):
    name: str
    endTime: datetime
    startTime: datetime
    problem_ids: list[int]


class ContestCreateResponse(BaseModel):
    id: int
    name: str
    slug: str
    message: str



class ContestInfoResponse(BaseModel):
    name: str
    slug: str
    startTime: datetime 
    endTime: datetime 
    created_by: int    
    problems: list["ContestInfoProblems"]