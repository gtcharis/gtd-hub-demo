from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, MentorProfile, MentorshipRequest, MentorshipConnection
from app.auth_dependencies import get_current_user, require_permission
from app.schemas.mentorship import MentorshipRequestCreate, MentorshipDecision

router = APIRouter(prefix="/mentorship", tags=["mentorship"])

def _scope(query, user: User):
    if user.role != "Programme Administrator":
        if user.institution_id is None:
            raise HTTPException(status_code=403, detail="Institution scope is not assigned")
        query = query.filter(MentorProfile.institution_id == user.institution_id)
    return query

def _request_payload(item: MentorshipRequest):
    profile = item.mentor_profile
    return {
        "id": item.id,
        "mentor_profile_id": profile.id,
        "member_user_id": item.member_user_id,
        "member_name": item.member.full_name,
        "mentor_user_id": profile.user_id,
        "mentor_name": profile.user.full_name,
        "mentor_title": profile.title,
        "message": item.message,
        "goals": item.goals,
        "status": item.status,
        "mentor_response": item.mentor_response,
        "created_at": item.created_at,
    }

@router.get("/mentors")
def list_mentors(
    q: str = Query(default="", max_length=120),
    expertise: str = Query(default="", max_length=80),
    accepting_only: bool = False,
    user: User = Depends(require_permission("mentorship:read")),
    db: Session = Depends(get_db),
):
    query = db.query(MentorProfile).options(joinedload(MentorProfile.user), joinedload(MentorProfile.institution))
    query = _scope(query, user)
    if accepting_only:
        query = query.filter(MentorProfile.accepting_requests.is_(True))
    profiles = query.order_by(MentorProfile.id).all()
    q_norm = q.strip().casefold()
    expertise_norm = expertise.strip().casefold()
    result = []
    for p in profiles:
        tags = [x.strip() for x in p.expertise.split(",") if x.strip()]
        searchable = " ".join([p.user.full_name, p.title, p.discipline, p.bio, *tags]).casefold()
        if q_norm and q_norm not in searchable:
            continue
        if expertise_norm and not any(expertise_norm in tag.casefold() for tag in tags):
            continue
        result.append({
            "id": p.id, "user_id": p.user_id, "name": p.user.full_name,
            "title": p.title, "discipline": p.discipline, "bio": p.bio,
            "expertise": tags, "institution_id": p.institution_id,
            "institution": p.institution.name, "accepting_requests": p.accepting_requests,
        })
    return result

@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_request(
    payload: MentorshipRequestCreate,
    user: User = Depends(require_permission("mentorship:request")),
    db: Session = Depends(get_db),
):
    if user.role != "Member":
        raise HTTPException(status_code=403, detail="Only Members can initiate mentorship requests")
    if user.institution_id is None:
        raise HTTPException(status_code=403, detail="Your account is not assigned to an institution")
    profile = db.query(MentorProfile).filter(MentorProfile.id == payload.mentor_profile_id).first()
    if profile is None or profile.institution_id != user.institution_id:
        raise HTTPException(status_code=404, detail="Mentor profile not found")
    if not profile.accepting_requests:
        raise HTTPException(status_code=409, detail="This mentor is not accepting requests")
    duplicate = db.query(MentorshipRequest).filter(
        MentorshipRequest.member_user_id == user.id,
        MentorshipRequest.mentor_profile_id == profile.id,
        MentorshipRequest.status.in_(["pending", "accepted"]),
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="You already have an open request with this mentor")
    item = MentorshipRequest(
        member_user_id=user.id, mentor_profile_id=profile.id,
        message=payload.message.strip(), goals=payload.goals.strip(),
        status="pending", created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    item = db.query(MentorshipRequest).options(
        joinedload(MentorshipRequest.member),
        joinedload(MentorshipRequest.mentor_profile).joinedload(MentorProfile.user),
    ).filter(MentorshipRequest.id == item.id).one()
    return _request_payload(item)

@router.get("/requests")
def list_requests(
    user: User = Depends(require_permission("mentorship:read")),
    db: Session = Depends(get_db),
):
    query = db.query(MentorshipRequest).options(
        joinedload(MentorshipRequest.member),
        joinedload(MentorshipRequest.mentor_profile).joinedload(MentorProfile.user),
    )
    if user.role == "Programme Administrator":
        pass
    elif user.role == "Mentor":
        query = query.join(MentorProfile).filter(MentorProfile.user_id == user.id)
    else:
        query = query.filter(MentorshipRequest.member_user_id == user.id)
    return [_request_payload(x) for x in query.order_by(MentorshipRequest.created_at.desc()).all()]

@router.post("/requests/{request_id}/decision")
def decide_request(
    request_id: int,
    payload: MentorshipDecision,
    user: User = Depends(require_permission("mentorship:manage_own")),
    db: Session = Depends(get_db),
):
    item = db.query(MentorshipRequest).options(
        joinedload(MentorshipRequest.member),
        joinedload(MentorshipRequest.mentor_profile).joinedload(MentorProfile.user),
    ).filter(MentorshipRequest.id == request_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Mentorship request not found")
    if user.role != "Programme Administrator" and item.mentor_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Mentorship request not found")
    if item.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending requests can be decided")
    item.status = payload.decision
    item.mentor_response = payload.response.strip() or None
    item.updated_at = datetime.now(timezone.utc)
    if payload.decision == "accepted":
        db.add(MentorshipConnection(
            request_id=item.id, member_user_id=item.member_user_id,
            mentor_user_id=item.mentor_profile.user_id, status="active",
            created_at=datetime.now(timezone.utc),
        ))
    db.commit()
    db.refresh(item)
    return _request_payload(item)

@router.post("/requests/{request_id}/cancel")
def cancel_request(
    request_id: int,
    user: User = Depends(require_permission("mentorship:request")),
    db: Session = Depends(get_db),
):
    item = db.query(MentorshipRequest).filter(
        MentorshipRequest.id == request_id,
        MentorshipRequest.member_user_id == user.id,
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Mentorship request not found")
    if item.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending requests can be cancelled")
    item.status = "cancelled"
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": item.id, "status": item.status}

@router.get("/connections")
def list_connections(
    user: User = Depends(require_permission("mentorship:read")),
    db: Session = Depends(get_db),
):
    query = db.query(MentorshipConnection).options(
        joinedload(MentorshipConnection.member),
        joinedload(MentorshipConnection.mentor),
    )
    if user.role == "Programme Administrator":
        pass
    elif user.role == "Mentor":
        query = query.filter(MentorshipConnection.mentor_user_id == user.id)
    else:
        query = query.filter(MentorshipConnection.member_user_id == user.id)
    return [{
        "id": c.id, "request_id": c.request_id,
        "member_user_id": c.member_user_id, "member_name": c.member.full_name,
        "mentor_user_id": c.mentor_user_id, "mentor_name": c.mentor.full_name,
        "status": c.status, "created_at": c.created_at,
    } for c in query.order_by(MentorshipConnection.created_at.desc()).all()]
