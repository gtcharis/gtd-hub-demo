"""expand workflow status column to 80
Revision ID: de08460b2cab
Revises: 25ac9d2abc53
Create Date: 2026-11-25 09:16:33.650420
"""
from alembic import op
import sqlalchemy as sa

revision = 'de08460b2cab'
down_revision = '25ac9d2abc53'
branch_labels = None
depends_on = None
def upgrade():
    op.alter_column(
        "secure_cases",
        "workflow_status",
        existing_type=sa.String(length=30),
        type_=sa.String(length=80),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "secure_cases",
        "workflow_status",
        existing_type=sa.String(length=80),
        type_=sa.String(length=30),
        existing_nullable=False,
    )