from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .contests import Contest, ContestPoints, ContestSubmission
    from .submission import Submission


class UserBase(SQLModel, table=False):
    id: int
    username: str
    provider: str
    provider_user_id: str
    email: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    contest_points: list["ContestPoints"] = Relationship(back_populates="user")
    contests: list["Contest"] = Relationship(back_populates="user")
    submissions: list["Submission"] = Relationship(back_populates="user")
    contests_submissions_link: list["ContestSubmission"] = Relationship(back_populates="user")


class UserWithId(UserBase, table=False):
    id: int
    password: str
    contest_points: list["ContestPoints"] = Relationship(back_populates="user")
    contests: list["Contest"] = Relationship(back_populates="user")
    submissions: list["Submission"] = Relationship(back_populates="user")
    contests_submissions_link: list["ContestSubmission"] = Relationship(back_populates="user")
