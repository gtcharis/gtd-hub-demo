"""Add administrative audit events for v0.3.5."""
from alembic import op
import sqlalchemy as sa

revision = "0007_administration_m_e"
down_revision = "0006_learning_library"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("details_json", sa.String(length=1200), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_admin_audit_events_actor_user_id", "admin_audit_events", ["actor_user_id"])
    op.create_index("ix_admin_audit_events_action", "admin_audit_events", ["action"])
    op.create_index("ix_admin_audit_events_institution_id", "admin_audit_events", ["institution_id"])
    op.create_index("ix_admin_audit_events_created_at", "admin_audit_events", ["created_at"])


def downgrade():
    op.drop_index("ix_admin_audit_events_created_at", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_institution_id", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_action", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_actor_user_id", table_name="admin_audit_events")
    op.drop_table("admin_audit_events")
