from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from enum import Enum


if TYPE_CHECKING:
    from .problem import Boilerplate
    from .submission import Submission

class Language(SQLModel, table=True):
    id : int | None= Field(default=None  , primary_key=True)
    judge0id: int
    name: str
    boilerplates: list["Boilerplate"] = Relationship(back_populates="language")
    submissions: list["Submission"] = Relationship(back_populates="language")

class LanguageCodes(str,Enum):
    cpp = "CPP"
    js = "JavaScript"
    py = "Python"
