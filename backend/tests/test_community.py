def test_member_can_create_discussion_and_reply(client, auth_headers):
    member = auth_headers("member@test.demo")
    created = client.post("/api/v1/community/discussions", headers=member, json={
        "title": "Building inclusive research networks",
        "category": "Research",
        "body": "What practical approaches have helped you build supportive research networks?",
    })
    assert created.status_code == 201, created.text
    discussion_id = created.json()["id"]
    reply = client.post(f"/api/v1/community/discussions/{discussion_id}/replies", headers=member,
                        json={"body": "Peer mentoring circles have been useful."})
    assert reply.status_code == 201, reply.text
    listed = client.get("/api/v1/community/discussions", headers=member)
    assert listed.status_code == 200
    item = next(x for x in listed.json() if x["id"] == discussion_id)
    assert item["reply_count"] == 1
    assert item["replies"][0]["body"] == "Peer mentoring circles have been useful."


def test_member_cannot_moderate_discussion(client, auth_headers):
    member = auth_headers("member2@test.demo")
    created = client.post("/api/v1/community/discussions", headers=member, json={
        "title": "Community learning exchange", "category": "General",
        "body": "Share an idea that has helped your learning community."
    })
    assert created.status_code == 201
    denied = client.patch(f"/api/v1/community/discussions/{created.json()['id']}/moderation",
                          headers=member, json={"status": "locked"})
    assert denied.status_code == 403


def test_moderator_can_lock_discussion(client, auth_headers):
    member = auth_headers("member3@test.demo")
    moderator = auth_headers("moderator@test.demo")
    created = client.post("/api/v1/community/discussions", headers=member, json={
        "title": "Respectful peer support spaces", "category": "Wellbeing",
        "body": "What helps make peer support discussions respectful and constructive?"
    })
    assert created.status_code == 201
    locked = client.patch(f"/api/v1/community/discussions/{created.json()['id']}/moderation",
                          headers=moderator, json={"status": "locked"})
    assert locked.status_code == 200
    reply = client.post(f"/api/v1/community/discussions/{created.json()['id']}/replies",
                        headers=member, json={"body": "This reply should be blocked."})
    assert reply.status_code == 409


def test_community_is_institution_scoped(client, auth_headers):
    member_a = auth_headers("member@test.demo")
    member_b = auth_headers("mentor-b@test.demo")
    created = client.post("/api/v1/community/discussions", headers=member_a, json={
        "title": "Institution A community discussion", "category": "General",
        "body": "This discussion should not appear in another institution."
    })
    assert created.status_code == 201
    result = client.get("/api/v1/community/discussions", headers=member_b)
    assert result.status_code == 200
    assert all(x["id"] != created.json()["id"] for x in result.json())
