"""Add database backed rate limiting for public enquiries.

Revision ID: 0002_inquiry_rate_limit
Revises: 0001_initial_schema
Create Date: 2026-10-20
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_inquiry_rate_limit"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inquiry_rate_limits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inquiry_rate_limits_ip_address", "inquiry_rate_limits", ["ip_address"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_inquiry_rate_limits_ip_address", table_name="inquiry_rate_limits")
    op.drop_table("inquiry_rate_limits")
