from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    username: str
    provider: str
    provider_user_id: str
    email : str| None = None
