"""Add Learning Library catalogue and audit records for v0.3.4."""
from alembic import op
import sqlalchemy as sa

revision = "0006_learning_library"
down_revision = "de08460b2cab"
branch_labels = None
depends_on = None

CATEGORIES = [
    ("Gender-Transformative Practice", "gender-transformative-practice", "Gender equality, inclusion and institutional change", 1),
    ("Mentorship & Leadership", "mentorship-leadership", "Mentorship, leadership and champion development", 2),
    ("Safe and Supportive Campuses", "safe-supportive-campuses", "Consent, support, safeguarding and safer learning spaces", 3),
    ("Inclusive STEM", "inclusive-stem", "Inclusive teaching, learning and STEM participation", 4),
    ("Research & Learning", "research-learning", "Research methods, learning materials and knowledge products", 5),
    ("Advocacy & Change", "advocacy-change", "Advocacy, policy engagement and change-making", 6),
]

def upgrade():
    op.create_table(
        "learning_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(300), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.String(1600), nullable=False, server_default=""),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("learning_categories.id"), nullable=False),
        sa.Column("resource_type", sa.String(40), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=True, unique=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("external_url", sa.String(1200), nullable=True),
        sa.Column("publisher", sa.String(180), nullable=True),
        sa.Column("keywords", sa.String(500), nullable=False, server_default=""),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("source_type IN ('upload', 'external_link')", name="ck_learning_resources_source_type"),
        sa.CheckConstraint("status IN ('draft', 'published', 'archived')", name="ck_learning_resources_status"),
    )
    op.create_index("ix_learning_resources_title", "learning_resources", ["title"])
    op.create_index("ix_learning_resources_category_id", "learning_resources", ["category_id"])
    op.create_index("ix_learning_resources_institution_id", "learning_resources", ["institution_id"])
    op.create_index("ix_learning_resources_status", "learning_resources", ["status"])
    op.create_table(
        "learning_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sequence", sa.Integer(), nullable=False, unique=True),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("learning_resources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("event_json", sa.Text(), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("event_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_learning_audit_events_resource_id", "learning_audit_events", ["resource_id"])
    op.create_index("ix_learning_audit_events_actor_user_id", "learning_audit_events", ["actor_user_id"])
    categories = sa.table("learning_categories", sa.column("name", sa.String), sa.column("slug", sa.String), sa.column("description", sa.String), sa.column("sort_order", sa.Integer), sa.column("is_active", sa.Boolean))
    op.bulk_insert(categories, [{"name": n, "slug": slug, "description": desc, "sort_order": order, "is_active": True} for n, slug, desc, order in CATEGORIES])

def downgrade():
    op.drop_table("learning_audit_events")
    op.drop_index("ix_learning_resources_status", table_name="learning_resources")
    op.drop_index("ix_learning_resources_institution_id", table_name="learning_resources")
    op.drop_index("ix_learning_resources_category_id", table_name="learning_resources")
    op.drop_index("ix_learning_resources_title", table_name="learning_resources")
    op.drop_table("learning_resources")
    op.drop_table("learning_categories")
