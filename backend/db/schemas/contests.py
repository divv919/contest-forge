from sqlmodel import SQLModel, Field, Relationship, TIMESTAMP
from datetime import datetime
from typing import ClassVar

class Contest(SQLModel,table=True):
    id: int | None = Field(default=None , primary_key=True)
    name: str
    startTime : datetime = Field(TIMESTAMP(timezone=True))
    endTime : datetime = Field(TIMESTAMP(timezone=True))
    created_by: int = Field(foreign_key="user.id", ondelete="CASCADE")

class ContestPoints(SQLModel, table=True):
    __tablename__ : ClassVar[str]= "contest_points"
    id: int| None = Field(default=None, primary_key=True)
    total_points: int
    rank: int
    user_id: int = Field(foreign_key="user.id" , ondelete="CASCADE")
    contest_id: int = Field(foreign_key="contest.id", ondelete="CASCADE")


class ContestProblems(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    solve_count: int = Field(default=0)
    problem_id: int= Field(foreign_key="problem.id" , ondelete="CASCADE")
    contest_id: int = Field(foreign_key="contest.id", ondelete="CASCADE")
    
class ContestSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submission.id", ondelete="CASCADE")
    contest_id : int = Field(foreign_key="contest.id", ondelete="CASCADE")
    problem_id : int = Field(foreign_key="problem.id", ondelete="CASCADE")