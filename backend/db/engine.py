from sqlmodel import create_engine

db_url = "postgresql+pg8000://judge0:judge0postgres@db:5432/judge0"

engine = create_engine(db_url, echo=True)
