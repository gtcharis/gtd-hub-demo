def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_demo_overview_requires_authentication(client):
    response = client.get("/api/v1/demo/overview")
    assert response.status_code == 401

def test_demo_overview_is_labelled_for_authenticated_user(client):
    login = client.post("/api/v1/auth/login", json={
        "email": "member@test.demo", "password": "TestPass!2026"
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    response = client.get("/api/v1/demo/overview", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Illustrative" in response.json()["data_label"]

def test_logout_revokes_session(client):
    login = client.post("/api/v1/auth/login", json={
        "email": "member@test.demo", "password": "TestPass!2026"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_role_guard_rejects_member_from_admin_endpoint(client):
    login = client.post("/api/v1/auth/login", json={
        "email": "member@test.demo", "password": "TestPass!2026"
    })
    token = login.json()["access_token"]
    response = client.get("/api/v1/admin/access-check", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
