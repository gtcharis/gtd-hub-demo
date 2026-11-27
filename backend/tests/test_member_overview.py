from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import (
    CommunityDiscussion,
    Institution,
    LearningCategory,
    LearningResource,
    MentorshipConnection,
    MentorshipRequest,
    MentorProfile,
    User,
)


def test_member_overview_returns_mixed_scope_metrics(client, auth_headers):
    with SessionLocal() as db:
        institution_a = db.query(Institution).filter_by(code="INST-A").one()
        institution_b = db.query(Institution).filter_by(code="INST-B").one()
        member = db.query(User).filter_by(email="member@test.demo").one()
        mentor = db.query(User).filter_by(email="mentor@test.demo").one()
        baseline_users = db.query(User).filter(User.institution_id.isnot(None)).count()
        baseline_connections = db.query(MentorshipConnection).filter_by(status="active").count()
        baseline_resources = db.query(LearningResource).filter(
            LearningResource.status == "published",
            (LearningResource.institution_id.is_(None))
            | (LearningResource.institution_id == institution_a.id),
        ).count()

        extra_member = User(
            email="overview-engagement@test.demo",
            full_name="Overview Engagement Member",
            role="Member",
            institution_id=institution_a.id,
            password_hash=member.password_hash,
            is_active=True,
        )
        db.add(extra_member)
        db.flush()

        category = LearningCategory(name="Overview Test", slug="overview-test", description="")
        db.add(category)
        db.flush()

        db.add_all([
            LearningResource(
                title="Programme resource", description="", category_id=category.id,
                resource_type="Guide", source_type="external_link", external_url="https://example.org/a",
                institution_id=None, status="published", created_by_user_id=mentor.id,
                updated_by_user_id=mentor.id,
            ),
            LearningResource(
                title="Institution resource", description="", category_id=category.id,
                resource_type="Guide", source_type="external_link", external_url="https://example.org/b",
                institution_id=institution_a.id, status="published", created_by_user_id=mentor.id,
                updated_by_user_id=mentor.id,
            ),
            LearningResource(
                title="Other institution resource", description="", category_id=category.id,
                resource_type="Guide", source_type="external_link", external_url="https://example.org/c",
                institution_id=institution_b.id, status="published", created_by_user_id=mentor.id,
                updated_by_user_id=mentor.id,
            ),
            LearningResource(
                title="Draft resource", description="", category_id=category.id,
                resource_type="Guide", source_type="external_link", external_url="https://example.org/d",
                institution_id=None, status="draft", created_by_user_id=mentor.id,
                updated_by_user_id=mentor.id,
            ),
        ])

        request = MentorshipRequest(
            member_user_id=extra_member.id,
            mentor_profile_id=db.query(MentorProfile).filter_by(user_id=mentor.id).one().id,
            message="Test request", goals="", status="accepted",
        )
        db.add(request)
        db.flush()
        db.add(MentorshipConnection(
            request_id=request.id, member_user_id=member.id,
            mentor_user_id=mentor.id, status="active",
        ))
        db.add(CommunityDiscussion(
            institution_id=institution_a.id, author_user_id=extra_member.id,
            title="Recent member activity", category="General", body="Synthetic test activity",
            status="open", created_at=datetime.now(timezone.utc) - timedelta(days=2),
            updated_at=datetime.now(timezone.utc),
        ))
        db.commit()

    response = client.get(
        "/api/v1/dashboard/member/overview",
        headers=auth_headers("member@test.demo"),
    )
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["registered_users"] == baseline_users + 1
    assert payload["mentorship_connections"] == baseline_connections + 1
    assert payload["resources_available"] == baseline_resources + 2
    assert payload["member_engagement"]["engaged_members"] >= 1
    assert payload["member_engagement"]["eligible_members"] >= 5
    assert payload["member_engagement"]["percentage"] > 0
    assert payload["metric_scopes"]["registered_users"] == "programme"
    assert payload["metric_scopes"]["member_engagement"] == "institution"

    with SessionLocal() as db:
        test_member = db.query(User).filter_by(email="overview-engagement@test.demo").one()
        db.delete(test_member)
        db.query(LearningResource).filter(LearningResource.title.in_([
            "Programme resource", "Institution resource",
            "Other institution resource", "Draft resource",
        ])).delete(synchronize_session=False)
        db.query(LearningCategory).filter_by(slug="overview-test").delete()
        db.commit()


def test_member_overview_is_not_available_to_non_members(client, auth_headers):
    response = client.get(
        "/api/v1/dashboard/member/overview",
        headers=auth_headers("mentor@test.demo"),
    )
    assert response.status_code == 403


def test_member_overview_requires_authentication(client):
    response = client.get("/api/v1/dashboard/member/overview")
    assert response.status_code == 401
