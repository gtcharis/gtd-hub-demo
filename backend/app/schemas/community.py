from pydantic import BaseModel, Field
from datetime import datetime
class DiscussionCreate(BaseModel):
    title: str = Field(min_length=8, max_length=180)
    category: str = Field(default="General", min_length=2, max_length=80)
    body: str = Field(min_length=20, max_length=5000)
class ReplyCreate(BaseModel):
    body: str = Field(min_length=2, max_length=3000)
class DiscussionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=8, max_length=180)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    body: str | None = Field(default=None, min_length=20, max_length=5000)
class ModerationUpdate(BaseModel):
    status: str = Field(pattern="^(open|locked|hidden)$")
