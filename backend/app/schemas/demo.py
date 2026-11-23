from typing import Literal
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    version: str

class OverviewResponse(BaseModel):
    members: int = Field(ge=0)
    mentorship_connections: int = Field(ge=0)
    resources: int = Field(ge=0)
    engagement_percent: int = Field(ge=0, le=100)
    data_label: str

class MentorRecord(BaseModel):
    id: str
    name: str
    field: str
    focus: str
    institution: str
