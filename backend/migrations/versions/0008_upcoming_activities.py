"""Add institution-scoped upcoming activities."""
from alembic import op
import sqlalchemy as sa

revision = "0008_upcoming_activities"
down_revision = "0007_administration_m_e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hub_activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.String(length=1200), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=40), nullable=False, server_default="Community"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(length=180), nullable=False, server_default=""),
        sa.Column("delivery_mode", sa.String(length=20), nullable=False, server_default="in_person"),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('draft', 'published', 'cancelled')", name="ck_hub_activities_status"),
        sa.CheckConstraint("end_at > start_at", name="ck_hub_activities_valid_time_range"),
    )
    op.create_index("ix_hub_activities_start_at", "hub_activities", ["start_at"])
    op.create_index("ix_hub_activities_institution_id", "hub_activities", ["institution_id"])
    op.create_index("ix_hub_activities_status", "hub_activities", ["status"])


def downgrade():
    op.drop_index("ix_hub_activities_status", table_name="hub_activities")
    op.drop_index("ix_hub_activities_institution_id", table_name="hub_activities")
    op.drop_index("ix_hub_activities_start_at", table_name="hub_activities")
    op.drop_table("hub_activities")
