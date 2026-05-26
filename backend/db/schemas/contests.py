
from datetime import datetime
from typing import ClassVar, TYPE_CHECKING
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .submission import Submission
    from .problem import Problem

class Contest(SQLModel, table=True):
    id: int | None = Field(default=None , primary_key=True)
    name: str
    startTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    endTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    created_by: int = Field(foreign_key="user.id", ondelete="CASCADE")

    contest_points: list[ContestPoints] = Relationship(back_populates="contest")
    contests_problems_link: list[ContestProblems] = Relationship(back_populates="contest")
    contests_submissions_link: list[ContestSubmission] = Relationship(back_populates="contest")
    submissions: list["Submission"] = Relationship(back_populates="active_contest")

    user: "User" = Relationship(back_populates="contests")
    

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
    points : int = Field(default=0)

    problem: "Problem" = Relationship(back_populates="contests_submissions_link")
    contest: Contest = Relationship(back_populates="contests_submissions_link")
    submission: "Submission" = Relationship(back_populates="contests_submissions_link")