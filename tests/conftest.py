import pytest
from sqlmodel import SQLModel,create_engine, Session
from fastapi.testclient import TestClient
from main import app
from app.schemas.models import User
from app.db.database import get_session
from app.core.security import get_password_hash


DATABASE_URL="postgresql+psycopg2://postgres:post1234waad@localhost:5433/pawbase_test"


engine = create_engine(DATABASE_URL,echo=False)

@pytest.fixture(scope='session',autouse=True)
def create_test_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture()
def session():
    with Session(engine) as session:
        yield session

@pytest.fixture()
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture()
def test_user(session):
    user = User(
        email='testwaad@gmail.com',
        password=get_password_hash('testshelter123'),
        role='org_admin'
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture()
def auth_token(client, test_user):
    response = client.post('/api/internal/auth/login',data={'username':test_user.email,'password':'testshelter123'}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    return response.json()['access_token']

@pytest.fixture()
def auth_client(client, auth_token):
    client.headers.update({'Authorization': f"Bearer {auth_token}"})
    return client




