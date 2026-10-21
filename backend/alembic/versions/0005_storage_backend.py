"""Track the backend used for each stored file."""

from alembic import op
import sqlalchemy as sa


revision = "0005_storage_backend"
down_revision = "0004_gallery_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "stored_files",
        sa.Column("storage_backend", sa.String(length=20), server_default="local", nullable=False),
    )
    op.alter_column("stored_files", "storage_backend", server_default=None)


def downgrade() -> None:
    op.drop_column("stored_files", "storage_backend")
