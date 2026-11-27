from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.auth_dependencies import require_permission
from app.database import get_db
from app.models import HubActivity, Institution, User
from app.schemas.activities import ActivityCreate, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["upcoming activities"])


def _manage_scope(user: User, institution_id: int | None):
    if user.role == "Programme Administrator":
        return
    if user.role == "Organisation Administrator" and institution_id == user.institution_id:
        return
    raise HTTPException(403, "You may only manage activities for your institution")


def _visible(query, user: User):
    if user.role != "Programme Administrator":
        if user.institution_id is None:
            raise HTTPException(403, "Institution scope is not assigned")
        query = query.filter(
            (HubActivity.institution_id.is_(None))
            | (HubActivity.institution_id == user.institution_id)
        )
    return query


def _out(item: HubActivity):
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "start_at": item.start_at,
        "end_at": item.end_at,
        "venue": item.venue,
        "delivery_mode": item.delivery_mode,
        "institution_id": item.institution_id,
        "institution_name": item.institution.name if item.institution else "Programme-wide",
        "status": item.status,
    }


@router.get("/upcoming")
def upcoming_activities(
    limit: int = Query(default=4, ge=1, le=12),
    user: User = Depends(require_permission("dashboard:read")),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    query = _visible(
        db.query(HubActivity)
        .options(joinedload(HubActivity.institution))
        .filter(
            HubActivity.status == "published",
            HubActivity.end_at > now,
        ),
        user,
    )
    return [_out(item) for item in query.order_by(HubActivity.start_at.asc()).limit(limit).all()]


@router.get("/manage")
def manage_activities(
    user: User = Depends(require_permission("administration:read")),
    db: Session = Depends(get_db),
):
    if user.role not in {"Organisation Administrator", "Programme Administrator"}:
        raise HTTPException(403, "Activity management is restricted")
    query = db.query(HubActivity).options(joinedload(HubActivity.institution))
    if user.role != "Programme Administrator":
        query = query.filter(HubActivity.institution_id == user.institution_id)
    return [_out(item) for item in query.order_by(HubActivity.start_at.desc()).all()]


@router.post("", status_code=201)
def create_activity(
    payload: ActivityCreate,
    user: User = Depends(require_permission("administration:read")),
    db: Session = Depends(get_db),
):
    if user.role not in {"Organisation Administrator", "Programme Administrator"}:
        raise HTTPException(403, "Activity management is restricted")
    _manage_scope(user, payload.institution_id)
    if payload.institution_id is not None:
        institution = db.query(Institution).filter(Institution.id == payload.institution_id, Institution.is_active.is_(True)).first()
        if institution is None:
            raise HTTPException(422, "A valid active institution is required")
    now = datetime.now(timezone.utc)
    item = HubActivity(**payload.model_dump(), created_by_user_id=user.id, updated_by_user_id=user.id, created_at=now, updated_at=now)
    db.add(item)
    db.commit()
    return _out(db.query(HubActivity).options(joinedload(HubActivity.institution)).filter(HubActivity.id == item.id).one())


@router.patch("/{activity_id}")
def update_activity(
    activity_id: int,
    payload: ActivityUpdate,
    user: User = Depends(require_permission("administration:read")),
    db: Session = Depends(get_db),
):
    if user.role not in {"Organisation Administrator", "Programme Administrator"}:
        raise HTTPException(403, "Activity management is restricted")
    item = db.query(HubActivity).filter(HubActivity.id == activity_id).first()
    if item is None:
        raise HTTPException(404, "Activity not found")
    _manage_scope(user, item.institution_id)
    changes = payload.model_dump(exclude_unset=True)
    target_institution = changes.get("institution_id", item.institution_id)
    _manage_scope(user, target_institution)
    if target_institution is not None:
        institution = db.query(Institution).filter(Institution.id == target_institution, Institution.is_active.is_(True)).first()
        if institution is None:
            raise HTTPException(422, "A valid active institution is required")
    new_start = changes.get("start_at", item.start_at)
    new_end = changes.get("end_at", item.end_at)
    if new_start is not None and new_end is not None and new_end <= new_start:
        raise HTTPException(422, "Activity end time must be after its start time")
    for key, value in changes.items():
        setattr(item, key, value)
    item.updated_by_user_id = user.id
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _out(db.query(HubActivity).options(joinedload(HubActivity.institution)).filter(HubActivity.id == item.id).one())
