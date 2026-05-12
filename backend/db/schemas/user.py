from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .contests import ContestPoints, Contest
class User(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    username: str
    provider: str
    provider_user_id: str
    email : str| None = None
    contest_points: list["ContestPoints"] = Relationship(back_populates="user")
    contests: list["Contest"] = Relationship(back_populates="user")
