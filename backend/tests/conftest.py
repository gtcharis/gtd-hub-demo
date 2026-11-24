import os
import pytest
from fastapi.testclient import TestClient

test_database_url = os.getenv("TEST_DATABASE_URL")
if not test_database_url:
    raise RuntimeError("Set TEST_DATABASE_URL to a dedicated PostgreSQL test database before running tests.")
from sqlalchemy.engine import make_url
_test_url = make_url(test_database_url)
if not _test_url.drivername.startswith("postgresql"):
    raise RuntimeError("TEST_DATABASE_URL must point to PostgreSQL.")
if not _test_url.database or "test" not in _test_url.database.lower():
    raise RuntimeError("Safety stop: TEST_DATABASE_URL database name must contain 'test'; tests drop and recreate all tables.")
if any(marker in _test_url.database.lower() for marker in ("prod", "production", "railway")):
    raise RuntimeError("Safety stop: production-like database names are not permitted for tests.")
os.environ["DATABASE_URL"] = test_database_url

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import Institution, User, MentorProfile
from app.security import hash_password

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if engine.dialect.name != "postgresql":
        raise RuntimeError("GTD Hub tests require PostgreSQL; SQLite is not supported.")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        b = Institution(name="Bindura University (Test)", code="BUSE-TEST")
        a = Institution(name="Test Institution A", code="INST-A")
        c = Institution(name="Test Institution B", code="INST-B")
        db.add_all([b, a, c])
        db.flush()
        password = hash_password("TestPass!2026")
        users = [
            ("member@test.demo", "Test Member", "Member", a.id),
            ("member2@test.demo", "Test Member Two", "Member", a.id),
            ("member3@test.demo", "Test Member Three", "Member", a.id),
            ("member4@test.demo", "Test Member Four", "Member", a.id),
            ("mentor@test.demo", "Test Mentor", "Mentor", a.id),
            ("moderator@test.demo", "Test Moderator", "Moderator", a.id),
            ("casehandler@test.demo", "Test Case Handler", "Case Handler", a.id),
            ("orgadmin@test.demo", "Test Organisation Admin", "Organisation Administrator", a.id),
            ("programmeadmin@test.demo", "Test Programme Admin", "Programme Administrator", None),
            ("orgadmin-b@test.demo", "Test Organisation Admin B", "Organisation Administrator", c.id),
            ("mentor-b@test.demo", "Test Mentor B", "Mentor", c.id),
        ]
        created = {}
        for email, name, role, institution_id in users:
            account = User(email=email, full_name=name, role=role, institution_id=institution_id, password_hash=password)
            db.add(account)
            created[email] = account
        db.flush()
        db.add(MentorProfile(
            user_id=created["mentor@test.demo"].id, institution_id=a.id,
            title="Research Mentor", discipline="Engineering",
            bio="Supports research and career development.",
            expertise="Research, Career, Engineering", accepting_requests=True,
        ))
        db.add(MentorProfile(
            user_id=created["mentor-b@test.demo"].id, institution_id=c.id,
            title="Second Institution Mentor", discipline="Science",
            bio="Supports academic development.",
            expertise="Academic, Science", accepting_requests=True,
        ))
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture()
def token_for(client):
    def issue(email):
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPass!2026"})
        assert response.status_code == 200, response.text
        return response.json()["access_token"]
    return issue

@pytest.fixture()
def auth_headers(token_for):
    def headers(email):
        return {"Authorization": f"Bearer {token_for(email)}"}
    return headers
