from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    institution_id: int | None
    institution_name: str | None
    is_active: bool
    permissions: list[str] = Field(default_factory=list)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
