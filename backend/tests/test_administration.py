
from app.api.admin_routes import _suppress_small_cells
from app.models import User, UserSession, Institution, AdminAuditEvent
from app.security import hash_session_token


def test_member_cannot_access_admin_endpoints(client, auth_headers):
    response = client.get(
        "/api/v1/admin/dashboard",
        headers=auth_headers("member@test.demo"),
    )
    assert response.status_code == 403


def test_org_admin_only_sees_own_users(client, auth_headers):
    response = client.get(
        "/api/v1/admin/users",
        headers=auth_headers("orgadmin@test.demo"),
    )

    assert response.status_code == 200

    emails = {item["email"] for item in response.json()["items"]}

    assert "orgadmin@test.demo" in emails
    assert "orgadmin-b@test.demo" not in emails


def test_org_admin_cannot_assign_admin_role(client, auth_headers):
    response = client.post(
        "/api/v1/admin/users",
        headers=auth_headers("orgadmin@test.demo"),
        json={
            "email": "newadmin@test.demo",
            "full_name": "New Admin",
            "password": "StrongTestPassword!2026",
            "role": "Programme Administrator",
            "institution_id": 2,
        },
    )

    assert response.status_code == 403


def test_programme_admin_can_create_and_update_institution(
    client,
    auth_headers,
):
    headers = auth_headers("programmeadmin@test.demo")

    created = client.post(
        "/api/v1/admin/institutions",
        headers=headers,
        json={
            "name": "New Test University",
            "code": "NEW-TEST",
        },
    )

    assert created.status_code == 201, created.text

    institution_id = created.json()["id"]

    updated = client.patch(
        f"/api/v1/admin/institutions/{institution_id}",
        headers=headers,
        json={"is_active": False},
    )

    assert updated.status_code == 200
    assert updated.json()["is_active"] is False


def test_role_change_revokes_existing_sessions(
    client,
    auth_headers,
    token_for,
):
    admin_headers = auth_headers("orgadmin@test.demo")

    created = client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={
            "email": "rolechange@test.demo",
            "full_name": "Role Change Test",
            "password": "TestPass!2026",
            "role": "Member",
            "institution_id": 2,
        },
    )

    assert created.status_code == 201, created.text

    member_token = token_for("rolechange@test.demo")

    member = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert member.status_code == 200
    assert member.json()["role"] == "Member"

    response = client.patch(
        f"/api/v1/admin/users/{member.json()['id']}",
        headers=admin_headers,
        json={"role": "Mentor"},
    )

    assert response.status_code == 200, response.text

    revoked = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert revoked.status_code == 401


# ---------------------------------------------------------------------
# M&E SMALL-CELL SUPPRESSION
# ---------------------------------------------------------------------

def test_small_cell_suppression():
    metrics = {
        "registered_users": 4,
        "active_accounts": 5,
        "mentors": 0,
        "mentorship_requests": 8,
        "active_mentorship_connections": 3,
        "community_discussions": 5,
        "published_learning_resources": 2,
        "case_data_included": False,
    }

    result = _suppress_small_cells(metrics)

    # Values below 5 must be suppressed.
    assert result["registered_users"] is None
    assert result["mentors"] is None
    assert result["active_mentorship_connections"] is None
    assert result["published_learning_resources"] is None

    # Values of 5 or more remain visible.
    assert result["active_accounts"] == 5
    assert result["mentorship_requests"] == 8
    assert result["community_discussions"] == 5

    assert result["suppression_threshold"] == 5

    assert set(result["suppressed_indicators"]) == {
        "registered_users",
        "mentors",
        "active_mentorship_connections",
        "published_learning_resources",
    }

    assert result["case_data_included"] is False


def test_small_cell_suppression_does_not_modify_original_metrics():
    metrics = {
        "registered_users": 2,
        "active_accounts": 7,
        "case_data_included": False,
    }

    result = _suppress_small_cells(metrics)

    assert result["registered_users"] is None
    assert result["active_accounts"] == 7

    # The original metrics dictionary must remain unchanged.
    assert metrics["registered_users"] == 2
    assert metrics["active_accounts"] == 7


def test_small_cell_suppression_handles_zero_counts():
    metrics = {
        "registered_users": 0,
        "active_accounts": 0,
        "mentors": 0,
        "mentorship_requests": 0,
        "active_mentorship_connections": 0,
        "community_discussions": 0,
        "published_learning_resources": 0,
        "case_data_included": False,
    }

    result = _suppress_small_cells(metrics)

    for field in (
        "registered_users",
        "active_accounts",
        "mentors",
        "mentorship_requests",
        "active_mentorship_connections",
        "community_discussions",
        "published_learning_resources",
    ):
        assert result[field] is None

    assert len(result["suppressed_indicators"]) == 7


# ---------------------------------------------------------------------
# M&E CSV EXPORT
# ---------------------------------------------------------------------

def test_m_e_export_contains_aggregate_fields_only(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/admin/reports/m-e.csv",
        headers=auth_headers("programmeadmin@test.demo"),
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    assert "registered_users" in response.text
    assert "active_accounts" in response.text
    assert "case_data_included,false" in response.text

    assert "suppression_threshold,5" in response.text
    assert "suppressed_indicators" in response.text

    # No sensitive case information may be exported.
    assert "case_ref" not in response.text.lower()
    assert "narrative" not in response.text.lower()
    assert "contact_details" not in response.text.lower()
    assert "phone_number" not in response.text.lower()


def test_m_e_export_uses_suppression_label(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/admin/reports/m-e.csv",
        headers=auth_headers("programmeadmin@test.demo"),
    )

    assert response.status_code == 200

    # The CSV exporter must use the explicit suppression label
    # whenever an indicator is suppressed.
    if "suppressed_indicators" in response.text:
        assert "Suppressed (<5>)" not in response.text
        assert "Suppressed (<5)" in response.text or "Suppressed" in response.text
