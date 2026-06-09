import pytest
from sqlmodel import Session, create_engine

from ..config import get_settings

settings = get_settings()

db_url = settings.database_url

engine = create_engine(db_url, echo=True)


@pytest.fixture(scope="session")
def session():
    with Session(engine) as session:
        yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from ..main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def token(client):
    response = client.post(
        "/auth/login", data={"username": "Divv919", "password": settings.demo_user_password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def headers(token):
    return {"Authorization": f"Bearer {token}"}
