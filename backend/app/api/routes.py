from fastapi import APIRouter, Depends
from app.schemas.demo import HealthResponse, OverviewResponse, MentorRecord
from app.auth_dependencies import get_current_user, require_roles
from app.models import User

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return {"status": "ok", "service": "gtd-hub-demo-api", "version": "0.2.4"}

@router.get("/demo/overview", response_model=OverviewResponse, tags=["demonstration"])
def demo_overview(user: User = Depends(get_current_user)):
    return {
        "members": 1248, "mentorship_connections": 362, "resources": 74,
        "engagement_percent": 86,
        "data_label": "Illustrative demonstration data",
    }

@router.get("/demo/mentors", response_model=list[MentorRecord], tags=["demonstration"])
def demo_mentors(user: User = Depends(get_current_user)):
    return [
        {"id": "M-01", "name": "Dr. R. Moyo", "field": "Engineering", "focus": "Research and career", "institution": "Demo institution"},
        {"id": "M-02", "name": "Mr. T. Ncube", "field": "Computer Science", "focus": "Academic development", "institution": "Demo institution"},
        {"id": "M-03", "name": "Ms. F. Dlamini", "field": "Data", "focus": "Leadership and wellbeing", "institution": "Demo institution"},
    ]


@router.get("/admin/access-check", tags=["administration"])
def administration_access(user: User = Depends(require_roles("Organisation Administrator", "Programme Administrator"))):
    return {"access_granted": True, "role": user.role}
