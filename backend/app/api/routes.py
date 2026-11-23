from fastapi import APIRouter
from app.schemas.demo import HealthResponse, OverviewResponse, MentorRecord

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return {"status": "ok", "service": "gtd-hub-demo-api", "version": "0.2.0"}

@router.get("/demo/overview", response_model=OverviewResponse, tags=["demonstration"])
def demo_overview():
    return {
        "members": 1248,
        "mentorship_connections": 362,
        "resources": 74,
        "engagement_percent": 86,
        "data_label": "Illustrative demonstration data"
    }

@router.get("/demo/mentors", response_model=list[MentorRecord], tags=["demonstration"])
def demo_mentors():
    return [
        {"id": "M-01", "name": "Dr. R. Moyo", "field": "Engineering", "focus": "Research and career", "institution": "Demo institution"},
        {"id": "M-02", "name": "Mr. T. Ncube", "field": "Computer Science", "focus": "Academic development", "institution": "Demo institution"},
        {"id": "M-03", "name": "Ms. F. Dlamini", "field": "Data", "focus": "Leadership and wellbeing", "institution": "Demo institution"}
    ]
