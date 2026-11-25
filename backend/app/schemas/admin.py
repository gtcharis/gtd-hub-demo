from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal

ROLES = (
    "Member", "Mentor", "Moderator", "Case Handler",
    "Organisation Administrator", "Programme Administrator",
)

class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=12, max_length=128)
    role: str
    institution_id: int | None = None

    @field_validator("role")
    @classmethod
    def valid_role(cls, value):
        if value not in ROLES:
            raise ValueError("Unsupported role")
        return value

class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    role: str | None = None
    institution_id: int | None = None
    is_active: bool | None = None

    @field_validator("role")
    @classmethod
    def valid_role(cls, value):
        if value is not None and value not in ROLES:
            raise ValueError("Unsupported role")
        return value

class InstitutionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")

class InstitutionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    code: str | None = Field(default=None, min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    is_active: bool | None = None
