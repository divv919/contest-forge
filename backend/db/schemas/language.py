from sqlmodel import SQLModel, Field

class Language(SQLModel, table=True):
    id : int | None= Field(default=None  , primary_key=True)
    judge0id: int
    name: str
