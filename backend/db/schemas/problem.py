from sqlmodel import SQLModel, Field , Relationship
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .contests import ContestProblems, ContestSubmission

class Difficulty(int, Enum):
    EASE="EASY"
    MEDIUM="MEDIUM"
    HARD="HARD"

class Problem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    solution: str
    slug: str
    test_cases_count: int = Field(default=0)
    difficulty: Difficulty
    contests_problems_link: list["ContestProblems"] = Relationship(back_populates="problem") 
    contests_submissions_link: list["ContestSubmission"] = Relationship(back_populates="problem")

class Boilerplate(SQLModel, table=True):
    problem_id : int = Field(foreign_key="problem.id", ondelete="CASCADE", primary_key=True)
    language_id: int = Field(foreign_key="language.id", ondelete="CASCADE",primary_key=True)
    boilerplate_code: str
    