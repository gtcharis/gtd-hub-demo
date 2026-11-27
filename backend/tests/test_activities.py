from datetime import datetime, timedelta, timezone


def _activity_payload(institution_id, *, title="Upcoming STEM activity", status="published"):
    start = datetime.now(timezone.utc) + timedelta(days=3)
    end = start + timedelta(hours=1)
    return {
        "title": title,
        "description": "A synthetic programme activity for testing.",
        "category": "Mentorship",
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
        "venue": "Main Hall",
        "delivery_mode": "in_person",
        "institution_id": institution_id,
        "status": status,
    }


def test_activity_create_and_upcoming_visibility(client, auth_headers):
    headers = auth_headers("programmeadmin@test.demo")
    created = client.post(
        "/api/v1/activities",
        json=_activity_payload(None),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    activity_id = created.json()["id"]

    member_items = client.get(
        "/api/v1/activities/upcoming",
        headers=auth_headers("member@test.demo"),
    )
    assert member_items.status_code == 200
    assert any(item["id"] == activity_id for item in member_items.json())

    other_institution_items = client.get(
        "/api/v1/activities/upcoming",
        headers=auth_headers("orgadmin-b@test.demo"),
    )
    assert other_institution_items.status_code == 200
    assert any(item["id"] == activity_id for item in other_institution_items.json())


def test_activity_institution_scope_and_draft_visibility(client, auth_headers):
    org_headers = auth_headers("orgadmin@test.demo")
    institution_id = client.get("/api/v1/institutions", headers=org_headers).json()[0]["id"]

    own = client.post(
        "/api/v1/activities",
        json=_activity_payload(institution_id, title="Institution-only activity"),
        headers=org_headers,
    )
    assert own.status_code == 201, own.text

    draft = client.post(
        "/api/v1/activities",
        json=_activity_payload(institution_id, title="Draft activity", status="draft"),
        headers=org_headers,
    )
    assert draft.status_code == 201, draft.text

    own_items = client.get("/api/v1/activities/upcoming", headers=auth_headers("member@test.demo"))
    assert any(item["id"] == own.json()["id"] for item in own_items.json())
    assert all(item["id"] != draft.json()["id"] for item in own_items.json())

    other_items = client.get("/api/v1/activities/upcoming", headers=auth_headers("orgadmin-b@test.demo"))
    assert all(item["id"] != own.json()["id"] for item in other_items.json())


def test_activity_management_is_role_and_institution_scoped(client, auth_headers):
    org_headers = auth_headers("orgadmin@test.demo")
    institution_id = client.get("/api/v1/institutions", headers=org_headers).json()[0]["id"]
    denied = client.post(
        "/api/v1/activities",
        json=_activity_payload(None, title="Forbidden global activity"),
        headers=org_headers,
    )
    assert denied.status_code == 403

    forbidden_role = client.post(
        "/api/v1/activities",
        json=_activity_payload(institution_id),
        headers=auth_headers("mentor@test.demo"),
    )
    assert forbidden_role.status_code == 403

    unauthenticated = client.get("/api/v1/activities/upcoming")
    assert unauthenticated.status_code == 401


def test_activity_rejects_invalid_time_range(client, auth_headers):
    payload = _activity_payload(None)
    payload["end_at"] = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/activities",
        json=payload,
        headers=auth_headers("programmeadmin@test.demo"),
    )
    assert response.status_code == 422
