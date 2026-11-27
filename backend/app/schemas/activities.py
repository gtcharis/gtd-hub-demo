from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ActivityCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(default="", max_length=1200)
    category: Literal["Mentorship", "Learning", "Community", "Programme"] = "Community"
    start_at: datetime
    end_at: datetime
    venue: str = Field(default="", max_length=180)
    delivery_mode: Literal["online", "in_person"] = "in_person"
    institution_id: int | None = None
    status: Literal["draft", "published"] = "draft"

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_at <= self.start_at:
            raise ValueError("Activity end time must be after its start time")
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("Activity dates must include a timezone")
        return self


class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=1200)
    category: Literal["Mentorship", "Learning", "Community", "Programme"] | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=180)
    delivery_mode: Literal["online", "in_person"] | None = None
    institution_id: int | None = None
    status: Literal["draft", "published", "cancelled"] | None = None

    @model_validator(mode="after")
    def validate_time_values(self):
        for value in (self.start_at, self.end_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("Activity dates must include a timezone")
        if self.start_at is not None and self.end_at is not None and self.end_at <= self.start_at:
            raise ValueError("Activity end time must be after its start time")
        return self
