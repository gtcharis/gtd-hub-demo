"""Add mentor profiles, requests and active connections."""
from alembic import op
import sqlalchemy as sa

revision = "0002_mentorship_workflow"
down_revision = "0001_auth_identity"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "mentor_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("discipline", sa.String(120), nullable=False),
        sa.Column("bio", sa.String(1200), nullable=False),
        sa.Column("expertise", sa.String(500), nullable=False, server_default=""),
        sa.Column("accepting_requests", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mentor_profiles_user_id", "mentor_profiles", ["user_id"])
    op.create_index("ix_mentor_profiles_institution_id", "mentor_profiles", ["institution_id"])
    op.create_table(
        "mentorship_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("member_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mentor_profile_id", sa.Integer(), sa.ForeignKey("mentor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.String(2000), nullable=False),
        sa.Column("goals", sa.String(1000), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("mentor_response", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for col in ("member_user_id", "mentor_profile_id", "status"):
        op.create_index(f"ix_mentorship_requests_{col}", "mentorship_requests", [col])
    op.create_table(
        "mentorship_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("mentorship_requests.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("member_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mentor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mentorship_connections_request_id", "mentorship_connections", ["request_id"])
    op.create_index("ix_mentorship_connections_member_user_id", "mentorship_connections", ["member_user_id"])
    op.create_index("ix_mentorship_connections_mentor_user_id", "mentorship_connections", ["mentor_user_id"])
    op.create_index("ix_mentorship_connections_status", "mentorship_connections", ["status"])

def downgrade():
    op.drop_table("mentorship_connections")
    op.drop_table("mentorship_requests")
    op.drop_table("mentor_profiles")
