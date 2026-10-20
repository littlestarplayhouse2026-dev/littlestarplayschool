"""Add admin-managed gallery images."""

import sqlalchemy as sa
from alembic import op

revision = "0004_gallery_items"
down_revision = "0003_username_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gallery_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("caption", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["stored_files.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id"),
    )
    op.create_index("ix_gallery_items_created_at", "gallery_items", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_gallery_items_created_at", table_name="gallery_items")
    op.drop_table("gallery_items")
