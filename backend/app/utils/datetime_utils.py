"""Datetime helper for dialect-compatible UTC timestamps."""

from datetime import datetime, timezone
from typing import Any


def get_db_now(db: Any = None) -> datetime:
    """Return timezone-aware UTC datetime for Postgres, or naive UTC for SQLite."""
    now = datetime.now(timezone.utc)
    if db is not None:
        bind = getattr(db, "bind", None)
        if bind is not None and getattr(getattr(bind, "dialect", None), "name", "") == "sqlite":
            return now.replace(tzinfo=None)
    return now

