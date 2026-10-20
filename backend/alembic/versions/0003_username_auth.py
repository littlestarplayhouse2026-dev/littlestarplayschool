"""Replace user email addresses with usernames.

Revision ID: 0003_username_auth
Revises: 0002_inquiry_rate_limit
Create Date: 2026-10-20
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_username_auth"
down_revision = "0002_inquiry_rate_limit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=100), nullable=True))
    op.execute(
        sa.text(
            """WITH candidates AS (
                   SELECT id,
                          COALESCE(NULLIF(left(lower(split_part(email, '@', 1)), 80), ''), 'user') AS base,
                          count(*) OVER (
                              PARTITION BY COALESCE(
                                  NULLIF(left(lower(split_part(email, '@', 1)), 80), ''),
                                  'user'
                              )
                          ) AS duplicates
                   FROM users
               )
               UPDATE users AS target
               SET username = CASE
                   WHEN candidates.duplicates > 1
                   THEN candidates.base || '_' || left(replace(candidates.id::text, '-', ''), 10)
                   ELSE candidates.base
               END
               FROM candidates
               WHERE target.id = candidates.id"""
        )
    )
    op.alter_column("users", "username", nullable=False)
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index(
        "uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True
    )


def downgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.execute(sa.text("UPDATE users SET email = username || '@users.invalid'"))
    op.alter_column("users", "email", nullable=False)
    op.drop_index("uq_users_username_lower", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
