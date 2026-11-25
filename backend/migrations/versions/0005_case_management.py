"""Add assignment history and encrypted structured case notes for v0.3.3."""
from alembic import op
import sqlalchemy as sa

revision = "0005_case_management"
down_revision = "0004_secure_case_data"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("secure_cases", sa.Column("assigned_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("secure_cases", sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("secure_cases", sa.Column("priority", sa.String(16), nullable=False, server_default="normal"))
    op.create_index("ix_secure_cases_assigned_to_user_id", "secure_cases", ["assigned_to_user_id"])
    op.create_check_constraint("ck_secure_cases_priority", "secure_cases", "priority IN ('low', 'normal', 'high', 'urgent')")
    op.create_table(
        "case_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_ref", sa.String(36), sa.ForeignKey("secure_cases.case_ref", ondelete="CASCADE"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("assigned_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_assignments_case_ref", "case_assignments", ["case_ref"])
    op.create_index("ix_case_assignments_institution_id", "case_assignments", ["institution_id"])
    op.create_table(
        "case_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_ref", sa.String(36), sa.ForeignKey("secure_cases.case_ref", ondelete="CASCADE"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("author_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note_code", sa.String(48), nullable=False),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_notes_case_ref", "case_notes", ["case_ref"])
    op.create_index("ix_case_notes_institution_id", "case_notes", ["institution_id"])


def downgrade():
    op.drop_table("case_notes")
    op.drop_table("case_assignments")
    op.drop_constraint("ck_secure_cases_priority", "secure_cases", type_="check")
    op.drop_index("ix_secure_cases_assigned_to_user_id", table_name="secure_cases")
    op.drop_column("secure_cases", "priority")
    op.drop_column("secure_cases", "assigned_at")
    op.drop_column("secure_cases", "assigned_to_user_id")
