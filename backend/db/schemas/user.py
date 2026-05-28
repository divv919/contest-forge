from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .contests import ContestPoints, Contest
    from .submission import Submission


class UserBase(SQLModel, table=False):
    id : int
    username: str
    provider: str
    provider_user_id: str
    email : str| None = None

class User(UserBase, table=True):
    id : int | None = Field(default=None, primary_key=True)
    password: str
    contest_points: list["ContestPoints"] = Relationship(back_populates="user")
    contests: list["Contest"] = Relationship(back_populates="user")
    submissions: list["Submission"] = Relationship(back_populates="user")

class UserWithId(UserBase, table=False):
    id : int 
    password: str
    contest_points: list["ContestPoints"] = Relationship(back_populates="user")
    contests: list["Contest"] = Relationship(back_populates="user")
    submissions: list["Submission"] = Relationship(back_populates="user")