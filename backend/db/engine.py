from sqlmodel import create_engine

from ..config import get_settings

settings = get_settings()

db_url = settings.database_url

engine = create_engine(db_url, echo=True)
