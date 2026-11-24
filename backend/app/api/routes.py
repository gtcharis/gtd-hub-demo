from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.demo import HealthResponse, OverviewResponse, MentorRecord
from app.auth_dependencies import require_permission
from app.models import User, Institution
from app.database import get_db
from app.role_policy import permissions_for_role, role_can_access_institution

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return {"status": "ok", "service": "gtd-hub-demo-api", "version": "0.3.0"}

@router.get("/demo/overview", response_model=OverviewResponse, tags=["demonstration"])
def demo_overview(user: User = Depends(require_permission("dashboard:read"))):
    return {
        "members": 1248, "mentorship_connections": 362, "resources": 74,
        "engagement_percent": 86,
        "data_label": "Illustrative demonstration data",
    }

@router.get("/demo/mentors", response_model=list[MentorRecord], tags=["demonstration"])
def demo_mentors(user: User = Depends(require_permission("mentorship:read"))):
    return [
        {"id": "M-01", "name": "Dr. R. Moyo", "field": "Engineering", "focus": "Research and career", "institution": "Demo institution"},
        {"id": "M-02", "name": "Mr. T. Ncube", "field": "Computer Science", "focus": "Academic development", "institution": "Demo institution"},
        {"id": "M-03", "name": "Ms. F. Dlamini", "field": "Data", "focus": "Leadership and wellbeing", "institution": "Demo institution"},
    ]

@router.get("/admin/access-check", tags=["administration"])
def administration_access(user: User = Depends(require_permission("administration:read"))):
    return {
        "access_granted": True,
        "role": user.role,
        "institution_id": user.institution_id,
        "permissions": sorted(permissions_for_role(user.role)),
        "scope": "all_institutions" if user.role == "Programme Administrator" else "own_institution",
    }

@router.get("/institutions", tags=["institutions"])
def list_institutions(
    user: User = Depends(require_permission("institution:read")),
    db: Session = Depends(get_db),
):
    query = db.query(Institution).filter(Institution.is_active.is_(True))
    if user.role != "Programme Administrator":
        if user.institution_id is None:
            raise HTTPException(status_code=403, detail="Institution scope is not assigned")
        query = query.filter(Institution.id == user.institution_id)
    return [
        {"id": item.id, "name": item.name, "code": item.code, "is_active": item.is_active}
        for item in query.order_by(Institution.name).all()
    ]

@router.get("/institutions/{institution_id}", tags=["institutions"])
def get_institution(
    institution_id: int,
    user: User = Depends(require_permission("institution:read")),
    db: Session = Depends(get_db),
):
    if not role_can_access_institution(user.role, user.institution_id, institution_id):
        raise HTTPException(status_code=403, detail="You do not have access to this institution")
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return {"id": institution.id, "name": institution.name, "code": institution.code, "is_active": institution.is_active}
