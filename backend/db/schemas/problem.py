from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .contests import ContestProblems, ContestSubmission
    from .language import Language
    from .submission import Submission


class Difficulty(str, Enum):
    EASE = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ProblemBase(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    difficulty: Difficulty
    slug: str


class Problem(ProblemBase, table=True):
    description: str
    solution: str
    test_cases_count: int = Field(default=0)
    contests_problems_link: list["ContestProblems"] = Relationship(back_populates="problem")
    contests_submissions_link: list["ContestSubmission"] = Relationship(back_populates="problem")
    boilerplates: list["Boilerplate"] = Relationship(back_populates="problem")
    submissions: list["Submission"] = Relationship(back_populates="problem")


class ProblemInfo(BaseModel):
    id: int | None = None
    name: str
    difficulty: Difficulty
    slug: str
    boilerplate_codes: dict[int, str]
    problem_metadata: str
    description: str


class Boilerplate(SQLModel, table=True):
    problem_id: int = Field(foreign_key="problem.id", ondelete="CASCADE", primary_key=True)
    language_id: int = Field(foreign_key="language.id", ondelete="CASCADE", primary_key=True)
    boilerplate_code: str
    problem: "Problem" = Relationship(back_populates="boilerplates")
    language: "Language" = Relationship(back_populates="boilerplates")


class ContestInfoProblems(ProblemBase):
    solve_count: int = 0
    attempted: str | None = None
