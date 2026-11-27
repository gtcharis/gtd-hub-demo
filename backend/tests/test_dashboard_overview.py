import pytest


ROLE_EXPECTED = {
    "member@test.demo": ["My mentorship requests", "Active mentorship connections", "Community discussions", "Learning resources"],
    "mentor@test.demo": ["Pending mentorship requests", "Active mentee connections", "Mentor profile", "Community discussions"],
    "moderator@test.demo": ["Open discussions", "Visible replies", "Hidden discussions", "Learning resources"],
    "casehandler@test.demo": ["Cases assigned to me", "Assigned cases in progress", "Assigned cases closed", "Unassigned institution queue"],
    "orgadmin@test.demo": ["Registered accounts", "Active accounts", "Active mentors", "Active mentorship connections"],
    "programmeadmin@test.demo": ["Registered accounts", "Active accounts", "Active institutions", "Active mentorship connections"],
}


@pytest.mark.parametrize("email", ROLE_EXPECTED)
def test_each_role_receives_its_own_database_backed_overview(client, auth_headers, email):
    response = client.get("/api/v1/dashboard/overview", headers=auth_headers(email))

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["role"]
    assert payload["scope"]
    assert payload["data_label"].startswith("Live aggregate counts")
    assert payload["case_data_included"] is False
    assert len(payload["metrics"]) == 4
    assert all(isinstance(metric["value"], int) for metric in payload["metrics"])
    assert [metric["label"] for metric in payload["metrics"]] == ROLE_EXPECTED[email]
    assert "case_ref" not in payload
    assert "narrative" not in payload


def test_overview_requires_authentication(client):
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401


def test_overview_rejects_invalid_bearer_session(client):
    # Identity and scope are derived exclusively from a valid bearer session.
    response = client.get(
        "/api/v1/dashboard/overview",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
