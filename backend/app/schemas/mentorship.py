from pydantic import BaseModel, Field
from datetime import datetime

class MentorshipRequestCreate(BaseModel):
    mentor_profile_id: int
    message: str = Field(min_length=10, max_length=2000)
    goals: str = Field(default="", max_length=1000)

class MentorshipDecision(BaseModel):
    decision: str = Field(pattern="^(accepted|declined)$")
    response: str = Field(default="", max_length=1000)

class MentorshipRequestOut(BaseModel):
    id: int
    mentor_profile_id: int
    member_user_id: int
    member_name: str
    mentor_user_id: int
    mentor_name: str
    mentor_title: str
    message: str
    goals: str
    status: str
    mentor_response: str | None
    created_at: datetime

class MentorProfileOut(BaseModel):
    id: int
    user_id: int
    name: str
    title: str
    discipline: str
    bio: str
    expertise: list[str]
    institution_id: int
    institution: str
    accepting_requests: bool

class MentorshipConnectionOut(BaseModel):
    id: int
    request_id: int
    member_user_id: int
    member_name: str
    mentor_user_id: int
    mentor_name: str
    status: str
    created_at: datetime
