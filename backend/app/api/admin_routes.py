
import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth_dependencies import require_permission
from app.database import get_db
from app.models import (
    AdminAuditEvent,
    CommunityDiscussion,
    Institution,
    LearningResource,
    MentorshipConnection,
    MentorshipRequest,
    User,
    UserSession,
)
from app.role_policy import role_can_access_institution
from app.schemas.admin import (
    AdminUserCreate,
    AdminUserUpdate,
    InstitutionCreate,
    InstitutionUpdate,
)
from app.security import hash_password


router = APIRouter(prefix="/admin", tags=["administration"])


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

# Counts below this threshold are suppressed in M&E reports.
ME_SMALL_CELL_THRESHOLD = 5


# ---------------------------------------------------------------------
# SHARED HELPERS
# ---------------------------------------------------------------------

def _scope(query, actor: User, column):
    """Apply institution scope unless the actor is a Programme Administrator."""
    if actor.role == "Programme Administrator":
        return query

    if actor.institution_id is None:
        raise HTTPException(
            status_code=403,
            detail="Institution scope is not assigned",
        )

    return query.filter(column == actor.institution_id)


def _validate_active_institution(db: Session, institution_id: int):
    """Return an institution only when it exists and is active."""
    institution = db.get(Institution, institution_id)

    if institution is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    if not institution.is_active:
        raise HTTPException(
            status_code=409,
            detail="Cannot assign an account to an inactive institution",
        )

    return institution


def _validate_user_scope(
    db: Session,
    actor: User,
    role: str,
    institution_id: int | None,
):
    """
    Validate the effective role and institution assignment.

    Organisation Administrators can only manage ordinary accounts
    within their own active institution.

    Programme Administrators can create programme-wide accounts
    and institution-scoped accounts.
    """
    if role == "Programme Administrator":
        if actor.role != "Programme Administrator":
            raise HTTPException(
                status_code=403,
                detail="Only Programme Administrators can assign this role",
            )

        if institution_id is not None:
            raise HTTPException(
                status_code=422,
                detail="Programme Administrator accounts must be programme-wide",
            )

        return None

    if institution_id is None:
        raise HTTPException(
            status_code=422,
            detail="An institution is required for this role",
        )

    if actor.role == "Organisation Administrator":
        if actor.institution_id is None:
            raise HTTPException(
                status_code=403,
                detail="Your account has no institution scope",
            )

        if institution_id != actor.institution_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage users in your own institution",
            )

    return _validate_active_institution(db, institution_id)


def _audit(
    db: Session,
    actor: User,
    action: str,
    target_type: str,
    target_id: str,
    institution_id: int | None,
    details: dict | None = None,
):
    """
    Record allowlisted administrative metadata.

    Do not include passwords, tokens, GBV narratives, case references,
    contact details or other sensitive case information.
    """
    safe = details or {}

    db.add(
        AdminAuditEvent(
            actor_user_id=actor.id,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            institution_id=institution_id,
            details_json=json.dumps(safe, separators=(",", ":"))[:1200],
        )
    )


def _user_payload(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "institution_id": user.institution_id,
        "institution_name": user.institution.name if user.institution else None,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def _institution_payload(item: Institution):
    return {
        "id": item.id,
        "name": item.name,
        "code": item.code,
        "is_active": item.is_active,
        "created_at": item.created_at,
    }


def _suppress_small_cells(metrics: dict) -> dict:
    """
    Suppress M&E counts below the reporting threshold.

    Suppressed values are represented as None in JSON responses.
    The CSV exporter converts them to an explicit suppression label.

    This is a basic small-cell safeguard, not comprehensive
    statistical disclosure control.
    """
    count_fields = (
        "registered_users",
        "active_accounts",
        "mentors",
        "mentorship_requests",
        "active_mentorship_connections",
        "community_discussions",
        "published_learning_resources",
    )

    result = dict(metrics)
    suppressed = []

    for field in count_fields:
        value = result.get(field)

        if value is not None and value < ME_SMALL_CELL_THRESHOLD:
            result[field] = None
            suppressed.append(field)

    result["suppressed_indicators"] = suppressed
    result["suppression_threshold"] = ME_SMALL_CELL_THRESHOLD

    return result


# ---------------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------------

@router.get("/users")
def list_users(
    q: str = Query(default="", max_length=120),
    role: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("organisation:manage_users")
    ),
):
    query = db.query(User).join(
        Institution,
        User.institution_id == Institution.id,
        isouter=True,
    )

    if actor.role != "Programme Administrator":
        if actor.institution_id is None:
            raise HTTPException(
                status_code=403,
                detail="Institution scope is not assigned",
            )

        query = query.filter(
            User.institution_id == actor.institution_id
        )

    if q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.filter(
            (func.lower(User.full_name).like(term))
            | (func.lower(User.email).like(term))
        )

    if role:
        query = query.filter(User.role == role)

    if active is not None:
        query = query.filter(User.is_active.is_(active))

    users = query.order_by(User.full_name).limit(500).all()

    return {
        "items": [_user_payload(user) for user in users],
        "count": len(users),
    }


@router.post("/users", status_code=201)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("organisation:manage_users")
    ),
):
    email = str(payload.email).strip().lower()

    existing = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    if actor.role == "Organisation Administrator":
        if payload.role in (
            "Organisation Administrator",
            "Programme Administrator",
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "Organisation Administrators cannot create "
                    "administrator accounts"
                ),
            )

    # Validate institution existence, activation and role scope
    # for both administrator types.
    _validate_user_scope(
        db=db,
        actor=actor,
        role=payload.role,
        institution_id=payload.institution_id,
    )

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        institution_id=payload.institution_id,
        is_active=True,
    )

    db.add(user)
    db.flush()

    _audit(
        db,
        actor,
        "user.created",
        "user",
        str(user.id),
        user.institution_id,
        {
            "role": user.role,
            "is_active": True,
        },
    )

    db.commit()
    db.refresh(user)

    return _user_payload(user)


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("organisation:manage_users")
    ),
):
    target = db.get(User, user_id)

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if actor.role == "Organisation Administrator":
        if target.institution_id != actor.institution_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage users in your own institution",
            )

        if target.role in (
            "Organisation Administrator",
            "Programme Administrator",
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot modify administrator accounts",
            )

        if payload.role in (
            "Organisation Administrator",
            "Programme Administrator",
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot assign administrator roles",
            )

        if (
            payload.institution_id is not None
            and payload.institution_id != actor.institution_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot move users outside your institution",
            )

    if target.id == actor.id and (
        payload.is_active is False
        or payload.role is not None
        or payload.institution_id is not None
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "You cannot deactivate or change the scope/role "
                "of your own account"
            ),
        )

    old_role = target.role
    old_institution = target.institution_id
    old_active = target.is_active

    # Determine the effective role and institution after this update.
    new_role = (
        payload.role
        if payload.role is not None
        else target.role
    )

    new_institution_id = (
        payload.institution_id
        if payload.institution_id is not None
        else target.institution_id
    )

    # Programme Administrator accounts must always be programme-wide.
    if new_role == "Programme Administrator":
        if actor.role != "Programme Administrator":
            raise HTTPException(
                status_code=403,
                detail="Only Programme Administrators can assign this role",
            )

        if payload.institution_id is not None:
            raise HTTPException(
                status_code=422,
                detail="Programme Administrator accounts must be programme-wide",
            )

        new_institution_id = None

    else:
        # Validate the effective institution even when the caller
        # changes only the role or other account details.
        _validate_user_scope(
            db=db,
            actor=actor,
            role=new_role,
            institution_id=new_institution_id,
        )

    if payload.full_name is not None:
        target.full_name = payload.full_name.strip()

    target.role = new_role
    target.institution_id = new_institution_id

    if payload.is_active is not None:
        target.is_active = payload.is_active

    changed_access = (
        old_role != target.role
        or old_institution != target.institution_id
        or old_active != target.is_active
    )

    if changed_access:
        now = datetime.now(timezone.utc)

        db.query(UserSession).filter(
            UserSession.user_id == target.id,
            UserSession.revoked_at.is_(None),
        ).update(
            {UserSession.revoked_at: now},
            synchronize_session=False,
        )

    details = {
        "old_role": old_role,
        "new_role": target.role,
        "old_institution_id": old_institution,
        "new_institution_id": target.institution_id,
        "old_is_active": old_active,
        "new_is_active": target.is_active,
    }

    _audit(
        db,
        actor,
        "user.updated",
        "user",
        str(target.id),
        target.institution_id,
        details,
    )

    db.commit()
    db.refresh(target)

    return _user_payload(target)


# ---------------------------------------------------------------------
# INSTITUTION MANAGEMENT
# ---------------------------------------------------------------------

@router.get("/institutions")
def admin_institutions(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("institution:read")),
):
    query = db.query(Institution)

    if actor.role != "Programme Administrator":
        if actor.institution_id is None:
            raise HTTPException(
                status_code=403,
                detail="Institution scope is not assigned",
            )

        query = query.filter(
            Institution.id == actor.institution_id
        )

    rows = query.order_by(Institution.name).all()

    return {
        "items": [_institution_payload(item) for item in rows],
        "count": len(rows),
    }


@router.post("/institutions", status_code=201)
def create_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("institution:manage_all")
    ),
):
    name = payload.name.strip()
    code = payload.code.strip().upper()

    duplicate = db.query(Institution).filter(
        (func.lower(Institution.name) == name.lower())
        | (func.lower(Institution.code) == code.lower())
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="An institution with this name or code already exists",
        )

    item = Institution(
        name=name,
        code=code,
        is_active=True,
    )

    db.add(item)
    db.flush()

    _audit(
        db,
        actor,
        "institution.created",
        "institution",
        str(item.id),
        item.id,
        {"code": item.code},
    )

    db.commit()
    db.refresh(item)

    return _institution_payload(item)


@router.patch("/institutions/{institution_id}")
def update_institution(
    institution_id: int,
    payload: InstitutionUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("institution:manage_all")
    ),
):
    item = db.get(Institution, institution_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    new_name = (
        payload.name.strip()
        if payload.name is not None
        else item.name
    )

    new_code = (
        payload.code.strip().upper()
        if payload.code is not None
        else item.code
    )

    duplicate = (
        db.query(Institution)
        .filter(Institution.id != item.id)
        .filter(
            (func.lower(Institution.name) == new_name.lower())
            | (func.lower(Institution.code) == new_code.lower())
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="An institution with this name or code already exists",
        )

    item.name = new_name
    item.code = new_code

    if payload.is_active is not None:
        item.is_active = payload.is_active

        if not item.is_active:
            now = datetime.now(timezone.utc)

            institution_user_ids = db.query(User.id).filter(
                User.institution_id == item.id
            )

            db.query(UserSession).filter(
                UserSession.user_id.in_(institution_user_ids),
                UserSession.revoked_at.is_(None),
            ).update(
                {UserSession.revoked_at: now},
                synchronize_session=False,
            )

    _audit(
        db,
        actor,
        "institution.updated",
        "institution",
        str(item.id),
        item.id,
        {"is_active": item.is_active},
    )

    db.commit()
    db.refresh(item)

    return _institution_payload(item)


# ---------------------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------------------

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("administration:read")),
):
    users = _scope(
        db.query(User),
        actor,
        User.institution_id,
    )

    institutions = db.query(Institution)

    if actor.role != "Programme Administrator":
        institutions = institutions.filter(
            Institution.id == actor.institution_id
        )

    mentors = _scope(
        db.query(User).filter(
            User.role == "Mentor",
            User.is_active.is_(True),
        ),
        actor,
        User.institution_id,
    )

    discussions = _scope(
        db.query(CommunityDiscussion),
        actor,
        CommunityDiscussion.institution_id,
    )

    connections = db.query(MentorshipConnection).join(
        User,
        User.id == MentorshipConnection.member_user_id,
    )

    if actor.role != "Programme Administrator":
        connections = connections.filter(
            User.institution_id == actor.institution_id
        )

    resources = db.query(LearningResource).filter(
        LearningResource.status == "published"
    )

    if actor.role != "Programme Administrator":
        resources = resources.filter(
            (LearningResource.institution_id == actor.institution_id)
            | (LearningResource.institution_id.is_(None))
        )

    return {
        "scope": (
            "programme"
            if actor.role == "Programme Administrator"
            else "institution"
        ),
        "institution_id": actor.institution_id,
        "users_total": users.count(),
        "users_active": users.filter(
            User.is_active.is_(True)
        ).count(),
        "institutions_total": institutions.count(),
        "mentors_active": mentors.count(),
        "community_discussions": discussions.count(),
        "mentorship_connections": connections.filter(
            MentorshipConnection.status == "active"
        ).count(),
        "published_learning_resources": resources.count(),
        "data_label": (
            "Demonstrator records; not programme evaluation findings"
        ),
    }


# ---------------------------------------------------------------------
# INSTITUTIONAL INSIGHTS
# ---------------------------------------------------------------------

@router.get("/insights")
def institutional_insights(
    institution_id: int | None = None,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("administration:read")),
):
    if institution_id is not None and not role_can_access_institution(
        actor.role,
        actor.institution_id,
        institution_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this institution",
        )

    scope_id = (
        institution_id
        if institution_id is not None
        else (
            None
            if actor.role == "Programme Administrator"
            else actor.institution_id
        )
    )

    if scope_id is not None and db.get(Institution, scope_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    users_q = db.query(User)
    discussions_q = db.query(CommunityDiscussion)

    connections_q = db.query(MentorshipConnection).join(
        User,
        User.id == MentorshipConnection.member_user_id,
    )

    requests_q = db.query(MentorshipRequest).join(
        User,
        User.id == MentorshipRequest.member_user_id,
    )

    resources_q = db.query(LearningResource).filter(
        LearningResource.status == "published"
    )

    if scope_id is not None:
        users_q = users_q.filter(
            User.institution_id == scope_id
        )

        discussions_q = discussions_q.filter(
            CommunityDiscussion.institution_id == scope_id
        )

        connections_q = connections_q.filter(
            User.institution_id == scope_id
        )

        requests_q = requests_q.filter(
            User.institution_id == scope_id
        )

        resources_q = resources_q.filter(
            (LearningResource.institution_id == scope_id)
            | (LearningResource.institution_id.is_(None))
        )

    metrics = {
        "scope": "institution" if scope_id else "programme",
        "institution_id": scope_id,
        "registered_users": users_q.count(),
        "active_accounts": users_q.filter(
            User.is_active.is_(True)
        ).count(),
        "mentors": users_q.filter(
            User.role == "Mentor",
            User.is_active.is_(True),
        ).count(),
        "mentorship_requests": requests_q.count(),
        "active_mentorship_connections": connections_q.filter(
            MentorshipConnection.status == "active"
        ).count(),
        "community_discussions": discussions_q.count(),
        "published_learning_resources": resources_q.count(),
        "case_data_included": False,
        "data_label": (
            "Aggregate counts from available demonstrator records; "
            "not a measure of participant outcomes"
        ),
    }

    return _suppress_small_cells(metrics)


# ---------------------------------------------------------------------
# ADMINISTRATIVE AUDIT VISIBILITY
# ---------------------------------------------------------------------

@router.get("/audit")
def admin_audit(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_permission("administration:audit")
    ),
):
    query = db.query(AdminAuditEvent)

    if actor.role != "Programme Administrator":
        if actor.institution_id is None:
            raise HTTPException(
                status_code=403,
                detail="Institution scope is not assigned",
            )

        query = query.filter(
            AdminAuditEvent.institution_id == actor.institution_id
        )

    events = query.order_by(
        AdminAuditEvent.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": event.id,
            "actor_user_id": event.actor_user_id,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "institution_id": event.institution_id,
            "details": json.loads(event.details_json),
            "created_at": event.created_at,
        }
        for event in events
    ]


# ---------------------------------------------------------------------
# AGGREGATE M&E CSV EXPORT
# ---------------------------------------------------------------------

@router.get("/reports/m-e.csv")
def export_me_report(
    institution_id: int | None = None,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("administration:read")),
):
    # Aggregate indicators only. No people, case references,
    # narratives or contact data are exported.
    metrics = institutional_insights(
        institution_id,
        db,
        actor,
    )

    _audit(
        db,
        actor,
        "report.exported",
        "report",
        "m-e-aggregate",
        metrics["institution_id"],
        {
            "scope": metrics["scope"],
            "format": "csv",
        },
    )

    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        ["indicator", "value", "scope", "institution_id"]
    )

    count_fields = (
        "registered_users",
        "active_accounts",
        "mentors",
        "mentorship_requests",
        "active_mentorship_connections",
        "community_discussions",
        "published_learning_resources",
    )

    for key in count_fields:
        value = metrics[key]

        if value is None:
            value = f"Suppressed (<{ME_SMALL_CELL_THRESHOLD})"

        writer.writerow(
            [
                key,
                value,
                metrics["scope"],
                metrics["institution_id"] or "programme",
            ]
        )

    writer.writerow(
        [
            "suppression_threshold",
            ME_SMALL_CELL_THRESHOLD,
            metrics["scope"],
            metrics["institution_id"] or "programme",
        ]
    )

    writer.writerow(
        [
            "suppressed_indicators",
            len(metrics["suppressed_indicators"]),
            metrics["scope"],
            metrics["institution_id"] or "programme",
        ]
    )

    writer.writerow(
        [
            "case_data_included",
            "false",
            metrics["scope"],
            metrics["institution_id"] or "programme",
        ]
    )

    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; filename=gtdhub-me-aggregate-report.csv"
            )
        },
    )
