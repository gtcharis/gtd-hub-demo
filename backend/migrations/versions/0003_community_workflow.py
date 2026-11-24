"""Add institution-scoped community discussions and replies."""
from alembic import op
import sqlalchemy as sa
revision = "0003_community_workflow"
down_revision = "0002_mentorship_workflow"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("community_discussions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("author_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("category", sa.String(80), nullable=False, server_default="General"),
        sa.Column("body", sa.String(5000), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    for col in ("institution_id", "author_user_id", "status"): op.create_index(f"ix_community_discussions_{col}", "community_discussions", [col])
    op.create_table("community_replies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("discussion_id", sa.Integer(), sa.ForeignKey("community_discussions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.String(3000), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="visible"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    for col in ("discussion_id", "author_user_id", "status"): op.create_index(f"ix_community_replies_{col}", "community_replies", [col])
def downgrade():
    op.drop_table("community_replies")
    op.drop_table("community_discussions")
