import pytest

ROLE_EMAILS = {
    "Member": "member@test.demo",
    "Mentor": "mentor@test.demo",
    "Moderator": "moderator@test.demo",
    "Case Handler": "casehandler@test.demo",
    "Organisation Administrator": "orgadmin@test.demo",
    "Programme Administrator": "programmeadmin@test.demo",
}

@pytest.mark.parametrize("role,email", ROLE_EMAILS.items())
def test_login_returns_role_permissions(client, role, email):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPass!2026"})
    assert response.status_code == 200
    user = response.json()["user"]
    assert user["role"] == role
    assert isinstance(user["permissions"], list)
    assert "dashboard:read" in user["permissions"]

def test_member_can_read_overview_and_cannot_read_admin(client, auth_headers):
    headers = auth_headers("member@test.demo")
    assert client.get("/api/v1/demo/overview", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/access-check", headers=headers).status_code == 403

def test_mentor_can_read_mentors(client, auth_headers):
    assert client.get("/api/v1/demo/mentors", headers=auth_headers("mentor@test.demo")).status_code == 200

def test_moderator_cannot_read_mentors(client, auth_headers):
    assert client.get("/api/v1/demo/mentors", headers=auth_headers("moderator@test.demo")).status_code == 403

def test_case_handler_cannot_access_admin(client, auth_headers):
    assert client.get("/api/v1/admin/access-check", headers=auth_headers("casehandler@test.demo")).status_code == 403

def test_org_admin_access_is_institution_scoped(client, auth_headers):
    headers = auth_headers("orgadmin@test.demo")
    response = client.get("/api/v1/institutions", headers=headers)
    assert response.status_code == 200
    assert [row["code"] for row in response.json()] == ["INST-A"]
    own = client.get("/api/v1/institutions/2", headers=headers)
    other = client.get("/api/v1/institutions/3", headers=headers)
    assert own.status_code == 200
    assert other.status_code == 403

def test_programme_admin_has_full_cross_institution_access(client, auth_headers):
    headers = auth_headers("programmeadmin@test.demo")
    response = client.get("/api/v1/institutions", headers=headers)
    assert response.status_code == 200
    codes = {row["code"] for row in response.json()}
    assert {"INST-A", "INST-B", "BUSE-TEST"} <= codes
    assert client.get("/api/v1/institutions/3", headers=headers).status_code == 200
    admin = client.get("/api/v1/admin/access-check", headers=headers)
    assert admin.status_code == 200
    assert admin.json()["scope"] == "all_institutions"

def test_organisation_admin_cannot_impersonate_other_institution_by_id(client, auth_headers):
    headers = auth_headers("orgadmin@test.demo")
    assert client.get("/api/v1/institutions/3", headers=headers).status_code == 403

def test_institutions_endpoint_requires_authentication(client):
    assert client.get("/api/v1/institutions").status_code == 401
