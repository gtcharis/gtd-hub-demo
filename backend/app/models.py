from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Institution(Base):
    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    users: Mapped[list["User"]] = relationship(back_populates="institution")

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(
            "role IN ('Member', 'Mentor', 'Moderator', 'Case Handler', 'Organisation Administrator', 'Programme Administrator')",
            name="ck_users_role",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    institution: Mapped[Institution | None] = relationship(back_populates="users")
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user: Mapped[User] = relationship(back_populates="sessions")


class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    discipline: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str] = mapped_column(String(1200), nullable=False)
    expertise: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    accepting_requests: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user: Mapped[User] = relationship()
    institution: Mapped[Institution] = relationship()


class MentorshipRequest(Base):
    __tablename__ = "mentorship_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    mentor_profile_id: Mapped[int] = mapped_column(ForeignKey("mentor_profiles.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(String(2000), nullable=False)
    goals: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    mentor_response: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    member: Mapped[User] = relationship(foreign_keys=[member_user_id])
    mentor_profile: Mapped[MentorProfile] = relationship()


class MentorshipConnection(Base):
    __tablename__ = "mentorship_connections"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("mentorship_requests.id", ondelete="CASCADE"), unique=True, index=True)
    member_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    mentor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    request: Mapped[MentorshipRequest] = relationship()
    member: Mapped[User] = relationship(foreign_keys=[member_user_id])
    mentor: Mapped[User] = relationship(foreign_keys=[mentor_user_id])


class CommunityDiscussion(Base):
    __tablename__ = "community_discussions"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="General")
    body: Mapped[str] = mapped_column(String(5000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    author: Mapped[User] = relationship()
    institution: Mapped[Institution] = relationship()
    replies: Mapped[list["CommunityReply"]] = relationship(back_populates="discussion", cascade="all, delete-orphan")

class CommunityReply(Base):
    __tablename__ = "community_replies"
    id: Mapped[int] = mapped_column(primary_key=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("community_discussions.id", ondelete="CASCADE"), index=True)
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(String(3000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="visible", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    author: Mapped[User] = relationship()
    discussion: Mapped[CommunityDiscussion] = relationship(back_populates="replies")

class SupportService(Base):
    __tablename__ = "support_services"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1200), nullable=False)
    contact_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class SecureCase(Base):
    __tablename__ = "secure_cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_ref: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    scenario_code: Mapped[str] = mapped_column(String(40), nullable=False)
    workflow_status: Mapped[str] = mapped_column(String(80), nullable=False, default="received")
    consent_status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_granted")
    ciphertext: Mapped[bytes] = mapped_column(nullable=False)
    nonce: Mapped[bytes] = mapped_column(nullable=False)
    key_version: Mapped[str] = mapped_column(String(20), nullable=False)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CaseAssignment(Base):
    __tablename__ = "case_assignments"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_ref: Mapped[str] = mapped_column(ForeignKey("secure_cases.case_ref", ondelete="CASCADE"), index=True, nullable=False)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True, nullable=False)
    assigned_to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CaseNote(Base):
    __tablename__ = "case_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_ref: Mapped[str] = mapped_column(ForeignKey("secure_cases.case_ref", ondelete="CASCADE"), index=True, nullable=False)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True, nullable=False)
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    note_code: Mapped[str] = mapped_column(String(48), nullable=False)
    ciphertext: Mapped[bytes] = mapped_column(nullable=False)
    nonce: Mapped[bytes] = mapped_column(nullable=False)
    key_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CaseAuditEvent(Base):
    __tablename__ = "case_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    sequence: Mapped[int] = mapped_column(nullable=False, unique=True)
    case_ref: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    institution_id: Mapped[int] = mapped_column(nullable=False, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(nullable=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    event_json: Mapped[str] = mapped_column(String(1200), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class LearningCategory(Base):
    __tablename__ = "learning_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class LearningResource(Base):
    __tablename__ = "learning_resources"
    __table_args__ = (
        CheckConstraint("source_type IN ('upload', 'external_link')", name="ck_learning_resources_source_type"),
        CheckConstraint("status IN ('draft', 'published', 'archived')", name="ck_learning_resources_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1600), nullable=False, default="")
    category_id: Mapped[int] = mapped_column(ForeignKey("learning_categories.id"), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True, unique=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(1200), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(180), nullable=True)
    keywords: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    category: Mapped[LearningCategory] = relationship()
    institution: Mapped[Institution | None] = relationship()

class LearningAuditEvent(Base):
    __tablename__ = "learning_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    sequence: Mapped[int] = mapped_column(nullable=False, unique=True)
    resource_id: Mapped[int | None] = mapped_column(ForeignKey("learning_resources.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    event_json: Mapped[str] = mapped_column(Text, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AdminAuditEvent(Base):
    """Administrative audit trail; deliberately excludes case-level content."""
    __tablename__ = "admin_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True, index=True)
    details_json: Mapped[str] = mapped_column(String(1200), nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class HubActivity(Base):
    __tablename__ = "hub_activities"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'cancelled')", name="ck_hub_activities_status"),
        CheckConstraint("end_at > start_at", name="ck_hub_activities_valid_time_range"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(String(1200), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="Community")
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    delivery_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="in_person")
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    institution: Mapped[Institution | None] = relationship()
    created_by: Mapped[User] = relationship(foreign_keys=[created_by_user_id])
    updated_by: Mapped[User] = relationship(foreign_keys=[updated_by_user_id])
