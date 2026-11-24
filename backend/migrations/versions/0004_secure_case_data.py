"""Encrypted support and safe-reporting case records with audit chain."""
from alembic import op
import sqlalchemy as sa
revision = "0004_secure_case_data"
down_revision = "0003_community_workflow"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("support_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.String(1200), nullable=False),
        sa.Column("contact_label", sa.String(160), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_support_services_institution_id", "support_services", ["institution_id"])
    # Non-operational directory placeholders: no unverified contacts or emergency numbers.
    support = sa.table("support_services", sa.column("institution_id", sa.Integer()), sa.column("category", sa.String()), sa.column("title", sa.String()), sa.column("description", sa.String()), sa.column("contact_label", sa.String()), sa.column("is_published", sa.Boolean()))
    op.bulk_insert(support, [
        {"institution_id": None, "category": "Information", "title": "Institutional gender support office", "description": "Illustrative directory entry. Each participating institution must confirm its designated office, referral pathway and contact details before publication for operational use.", "contact_label": "Contact details pending institutional verification", "is_published": True},
        {"institution_id": None, "category": "Psychosocial", "title": "Psychosocial support services", "description": "Illustrative directory entry. Service provider, eligibility, availability and referral consent process require verification by the project team.", "contact_label": "Provider details pending verification", "is_published": True},
        {"institution_id": None, "category": "Legal information", "title": "Legal information and advice", "description": "Illustrative directory entry only. No legal provider or referral relationship is represented by this entry.", "contact_label": "Provider details pending verification", "is_published": True},
    ])
    op.create_table("secure_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_ref", sa.String(36), nullable=False, unique=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("anonymous", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("scenario_code", sa.String(40), nullable=False),
        sa.Column("workflow_status", sa.String(30), nullable=False, server_default="received"),
        sa.Column("consent_status", sa.String(20), nullable=False, server_default="not_granted"),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    for col in ("case_ref", "institution_id", "created_by_user_id"):
        op.create_index(f"ix_secure_cases_{col}", "secure_cases", [col], unique=(col == "case_ref"))
    op.create_table("case_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sequence", sa.Integer(), nullable=False, unique=True),
        sa.Column("case_ref", sa.String(36), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("event_json", sa.String(1200), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("event_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_case_audit_events_case_ref", "case_audit_events", ["case_ref"])
    op.create_index("ix_case_audit_events_institution_id", "case_audit_events", ["institution_id"])

def downgrade():
    op.drop_table("case_audit_events")
    op.drop_table("secure_cases")
    op.drop_table("support_services")
