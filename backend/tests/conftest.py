import os
os.environ["DATABASE_URL"] = "sqlite:///./test_gtdhub_auth.db"

import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import Institution, User
from app.security import hash_password

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        institution = Institution(name="Test University", code="TEST")
        db.add(institution)
        db.flush()
        db.add(User(
            email="member@test.demo", full_name="Test Member", role="Member",
            institution_id=institution.id, password_hash=hash_password("TestPass!2026"),
        ))
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
