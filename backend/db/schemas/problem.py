from sqlmodel import SQLModel, Field
from enum import Enum

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

class Boilerplate(SQLModel, table=True):
    id: int |None = Field(default=None, primary_key=True)
    problem_id : int = Field(foreign_key="problem.id", ondelete="CASCADE")
    language_id: int = Field(foreign_key="language.id", ondelete="CASCADE")
    boilerplate_code: str
    