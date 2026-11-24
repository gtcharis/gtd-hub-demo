def test_member_can_discover_institution_mentors(client, auth_headers):
    response = client.get("/api/v1/mentorship/mentors", headers=auth_headers("member@test.demo"))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Mentor"


def test_member_can_create_request_and_mentor_can_accept(client, auth_headers):
    member_headers = auth_headers("member2@test.demo")
    mentor_headers = auth_headers("mentor@test.demo")
    mentors = client.get("/api/v1/mentorship/mentors", headers=member_headers).json()
    response = client.post(
        "/api/v1/mentorship/requests",
        headers=member_headers,
        json={
            "mentor_profile_id": mentors[0]["id"],
            "message": "I would appreciate guidance on my research pathway.",
            "goals": "Build research confidence and plan a career.",
        },
    )
    assert response.status_code == 201, response.text
    request_id = response.json()["id"]
    assert response.json()["status"] == "pending"

    inbox = client.get("/api/v1/mentorship/requests", headers=mentor_headers)
    assert inbox.status_code == 200
    assert inbox.json()[0]["id"] == request_id

    decision = client.post(
        f"/api/v1/mentorship/requests/{request_id}/decision",
        headers=mentor_headers,
        json={"decision": "accepted", "response": "Happy to support your goals."},
    )
    assert decision.status_code == 200, decision.text
    assert decision.json()["status"] == "accepted"

    member_connections = client.get("/api/v1/mentorship/connections", headers=member_headers)
    assert member_connections.status_code == 200
    assert len(member_connections.json()) == 1
    assert member_connections.json()[0]["mentor_name"] == "Test Mentor"


def test_member_cannot_decide_mentorship_request(client, auth_headers):
    member_headers = auth_headers("member3@test.demo")
    mentors = client.get("/api/v1/mentorship/mentors", headers=member_headers).json()
    created = client.post(
        "/api/v1/mentorship/requests",
        headers=member_headers,
        json={"mentor_profile_id": mentors[0]["id"], "message": "Please guide me with my studies."},
    )
    assert created.status_code == 201
    response = client.post(
        f"/api/v1/mentorship/requests/{created.json()['id']}/decision",
        headers=member_headers,
        json={"decision": "accepted"},
    )
    assert response.status_code == 403


def test_mentor_cannot_decide_another_mentors_request(client, auth_headers):
    member_headers = auth_headers("member4@test.demo")
    other_mentor_headers = auth_headers("mentor-b@test.demo")
    mentors = client.get("/api/v1/mentorship/mentors", headers=member_headers).json()
    created = client.post(
        "/api/v1/mentorship/requests",
        headers=member_headers,
        json={"mentor_profile_id": mentors[0]["id"], "message": "Please guide me with my studies."},
    )
    assert created.status_code == 201
    response = client.post(
        f"/api/v1/mentorship/requests/{created.json()['id']}/decision",
        headers=other_mentor_headers,
        json={"decision": "accepted"},
    )
    assert response.status_code == 404


def test_member_cannot_discover_other_institution_mentors(client, auth_headers):
    response = client.get("/api/v1/mentorship/mentors", headers=auth_headers("member@test.demo"))
    assert response.status_code == 200
    assert all(item["institution"] == "Test Institution A" for item in response.json())
