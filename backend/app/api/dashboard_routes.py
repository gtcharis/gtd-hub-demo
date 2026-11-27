"""Role-aware, database-backed overview metrics for GTD Hub.

Only aggregate operational counts are returned. Secure case narratives,
case references, consent details and identifiable case-level records are
never included in dashboard responses.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, union
from sqlalchemy.orm import Session

from app.auth_dependencies import require_permission
from app.database import get_db
from app.models import (
    CommunityDiscussion,
    CommunityReply,
    Institution,
    LearningResource,
    MentorProfile,
    MentorshipConnection,
    MentorshipRequest,
    SecureCase,
    User,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _institution_required(user: User) -> int:
    if user.institution_id is None:
        raise HTTPException(status_code=403, detail="Institution scope is not assigned")
    return user.institution_id


def _published_resources_query(db: Session, institution_id: int | None):
    query = db.query(LearningResource).filter(LearningResource.status == "published")
    if institution_id is not None:
        query = query.filter(
            (LearningResource.institution_id == institution_id)
            | (LearningResource.institution_id.is_(None))
        )
    return query


def _discussion_query(db: Session, institution_id: int | None):
    query = db.query(CommunityDiscussion).filter(CommunityDiscussion.status != "hidden")
    if institution_id is not None:
        query = query.filter(CommunityDiscussion.institution_id == institution_id)
    return query


def _metric(label: str, value: int):
    return {"label": label, "value": int(value)}


def _member_engagement(db: Session, institution_id: int, window_days: int = 30) -> dict:
    """Count institution members with at least one meaningful action in the rolling window.

    Supported actions are creating a visible discussion, posting a visible reply,
    submitting a mentorship request, or starting a mentorship connection. Resource
    views are not counted because the current data model does not record them.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    eligible_query = db.query(User.id).filter(
        User.institution_id == institution_id,
        User.role == "Member",
        User.is_active.is_(True),
    )
    eligible_members = eligible_query.count()

    activity_queries = [
        select(User.id.label("user_id"))
        .join(CommunityDiscussion, CommunityDiscussion.author_user_id == User.id)
        .where(
            User.institution_id == institution_id,
            User.role == "Member",
            User.is_active.is_(True),
            CommunityDiscussion.created_at >= cutoff,
            CommunityDiscussion.status != "hidden",
        ),
        select(User.id.label("user_id"))
        .join(CommunityReply, CommunityReply.author_user_id == User.id)
        .join(CommunityDiscussion, CommunityDiscussion.id == CommunityReply.discussion_id)
        .where(
            User.institution_id == institution_id,
            User.role == "Member",
            User.is_active.is_(True),
            CommunityReply.created_at >= cutoff,
            CommunityReply.status == "visible",
            CommunityDiscussion.status != "hidden",
        ),
        select(User.id.label("user_id"))
        .join(MentorshipRequest, MentorshipRequest.member_user_id == User.id)
        .where(
            User.institution_id == institution_id,
            User.role == "Member",
            User.is_active.is_(True),
            MentorshipRequest.created_at >= cutoff,
        ),
        select(User.id.label("user_id"))
        .join(MentorshipConnection, MentorshipConnection.member_user_id == User.id)
        .where(
            User.institution_id == institution_id,
            User.role == "Member",
            User.is_active.is_(True),
            MentorshipConnection.created_at >= cutoff,
        ),
    ]
    active_members = union(*activity_queries).subquery("recent_member_activity")
    engaged_members = db.query(active_members.c.user_id).distinct().count()
    percentage = round((engaged_members / eligible_members) * 100, 1) if eligible_members else 0.0

    return {
        "engaged_members": engaged_members,
        "eligible_members": eligible_members,
        "percentage": percentage,
        "window_days": window_days,
        "definition": "At least one visible community discussion or reply, mentorship request, or mentorship connection created in the last 30 days.",
        "activity_types": [
            "community_discussion",
            "community_reply",
            "mentorship_request",
            "mentorship_connection",
        ],
    }


def _member_programme_metrics(db: Session, institution_id: int) -> dict:
    registered_users = db.query(User).filter(User.institution_id.isnot(None)).count()
    active_connections = db.query(MentorshipConnection).filter(
        MentorshipConnection.status == "active"
    ).count()
    resources_available = _published_resources_query(db, institution_id).count()
    return {
        "registered_users": registered_users,
        "mentorship_connections": active_connections,
        "resources_available": resources_available,
        "member_engagement": _member_engagement(db, institution_id),
        "metric_scopes": {
            "registered_users": "programme",
            "mentorship_connections": "programme",
            "resources_available": "programme_and_institution",
            "member_engagement": "institution",
        },
    }


@router.get("/overview")
def role_overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("dashboard:read")),
):
    """Return metrics tailored to the authenticated role and its data scope."""
    role = user.role
    institution_id = None if role == "Programme Administrator" else _institution_required(user)
    metrics: list[dict] = []
    member_programme_data = None

    if role == "Member":
        member_programme_data = _member_programme_metrics(db, institution_id)
        requests = db.query(MentorshipRequest).filter(MentorshipRequest.member_user_id == user.id)
        connections = db.query(MentorshipConnection).filter(
            MentorshipConnection.member_user_id == user.id,
            MentorshipConnection.status == "active",
        )
        metrics = [
            _metric("My mentorship requests", requests.count()),
            _metric("Active mentorship connections", connections.count()),
            _metric("Community discussions", _discussion_query(db, institution_id).count()),
            _metric("Learning resources", _published_resources_query(db, institution_id).count()),
        ]
        description = "Your mentorship activity and the learning and community spaces available to you."

    elif role == "Mentor":
        profile = db.query(MentorProfile).filter(MentorProfile.user_id == user.id).first()
        pending = 0
        if profile is not None:
            pending = db.query(MentorshipRequest).filter(
                MentorshipRequest.mentor_profile_id == profile.id,
                MentorshipRequest.status == "pending",
            ).count()
        connections = db.query(MentorshipConnection).filter(
            MentorshipConnection.mentor_user_id == user.id,
            MentorshipConnection.status == "active",
        ).count()
        metrics = [
            _metric("Pending mentorship requests", pending),
            _metric("Active mentee connections", connections),
            _metric("Mentor profile", 1 if profile is not None else 0),
            _metric("Community discussions", _discussion_query(db, institution_id).count()),
        ]
        description = "Your mentorship requests, active connections and institutional community activity."

    elif role == "Moderator":
        discussions = db.query(CommunityDiscussion).filter(
            CommunityDiscussion.institution_id == institution_id
        )
        visible_discussions = discussions.filter(CommunityDiscussion.status != "hidden")
        visible_replies = db.query(CommunityReply).join(
            CommunityDiscussion,
            CommunityReply.discussion_id == CommunityDiscussion.id,
        ).filter(
            CommunityDiscussion.institution_id == institution_id,
            CommunityReply.status == "visible",
            CommunityDiscussion.status != "hidden",
        )
        metrics = [
            _metric("Open discussions", visible_discussions.filter(CommunityDiscussion.status == "open").count()),
            _metric("Visible replies", visible_replies.count()),
            _metric("Hidden discussions", discussions.filter(CommunityDiscussion.status == "hidden").count()),
            _metric("Learning resources", _published_resources_query(db, institution_id).count()),
        ]
        description = "A snapshot of discussion activity and moderation actions within your institution."

    elif role == "Case Handler":
        assigned = db.query(SecureCase).filter(
            SecureCase.institution_id == institution_id,
            SecureCase.assigned_to_user_id == user.id,
        )
        institution_queue = db.query(SecureCase).filter(
            SecureCase.institution_id == institution_id,
            SecureCase.assigned_to_user_id.is_(None),
        )
        metrics = [
            _metric("Cases assigned to me", assigned.count()),
            _metric("Assigned cases in progress", assigned.filter(SecureCase.workflow_status != "closed").count()),
            _metric("Assigned cases closed", assigned.filter(SecureCase.workflow_status == "closed").count()),
            _metric("Unassigned institution queue", institution_queue.count()),
        ]
        description = "Aggregate workload indicators for your assigned synthetic demonstration cases."

    elif role == "Organisation Administrator":
        users = db.query(User).filter(User.institution_id == institution_id)
        connections = db.query(MentorshipConnection).join(
            User, User.id == MentorshipConnection.member_user_id
        ).filter(User.institution_id == institution_id, MentorshipConnection.status == "active")
        metrics = [
            _metric("Registered accounts", users.count()),
            _metric("Active accounts", users.filter(User.is_active.is_(True)).count()),
            _metric("Active mentors", users.filter(User.role == "Mentor", User.is_active.is_(True)).count()),
            _metric("Active mentorship connections", connections.count()),
        ]
        description = "Institution-scoped participation and service indicators for your organisation."

    elif role == "Programme Administrator":
        users = db.query(User)
        metrics = [
            _metric("Registered accounts", users.count()),
            _metric("Active accounts", users.filter(User.is_active.is_(True)).count()),
            _metric("Active institutions", db.query(Institution).filter(Institution.is_active.is_(True)).count()),
            _metric("Active mentorship connections", db.query(MentorshipConnection).filter(MentorshipConnection.status == "active").count()),
        ]
        description = "Programme-wide aggregate indicators across participating institutions."

    else:  # Defensive guard if a role is added without dashboard design.
        raise HTTPException(status_code=403, detail="No overview dashboard is configured for this role")

    payload = {
        "role": role,
        "scope": "programme" if role == "Programme Administrator" else "institution" if role == "Organisation Administrator" else "personal" if role in ("Member", "Mentor") else "institutional_workload" if role in ("Moderator", "Case Handler") else "institution",
        "institution_id": institution_id,
        "title": "Your overview",
        "description": description,
        "metrics": metrics,
        "data_label": "Live aggregate counts from the GTD Hub demonstration database",
        "case_data_included": False,
    }
    if member_programme_data is not None:
        payload.update(member_programme_data)
    return payload


@router.get("/member/overview")
def member_overview_compatibility(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("dashboard:read")),
):
    """Backward-compatible member endpoint; non-members are explicitly denied."""
    if user.role != "Member":
        raise HTTPException(status_code=403, detail="Member overview is available to Members only")
    return role_overview(db=db, user=user)
