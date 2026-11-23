from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_demo_overview_is_labelled():
    response = client.get("/api/v1/demo/overview")
    assert response.status_code == 200
    assert "Illustrative" in response.json()["data_label"]
