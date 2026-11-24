from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
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
