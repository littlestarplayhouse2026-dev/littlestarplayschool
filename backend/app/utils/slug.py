"""Slug generation utility."""

import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _slugify_text(text: str) -> str:
    """Convert arbitrary text into a URL-safe slug.

    - Normalises unicode to ASCII approximations
    - Lowercases
    - Replaces non-alphanumeric chars with hyphens
    - Strips leading/trailing hyphens and collapses duplicates
    """
    # Normalize unicode to decomposed form, strip accents
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    # Replace any non-alphanumeric character with a hyphen
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Collapse multiple hyphens, strip leading/trailing
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled"


async def generate_unique_slug(
    title: str,
    model_class: type,
    db: AsyncSession,
    existing_id: str | None = None,
) -> str:
    """Generate a unique slug for a given title within the provided model's table.

    If the slug already exists (for a different record), appends -2, -3, etc.

    Args:
        title: The title to slugify.
        model_class: The SQLAlchemy model class (must have a `slug` column and `id` column).
        db: The async database session.
        existing_id: If updating, the ID of the current record (so it doesn't conflict with itself).

    Returns:
        A unique slug string.
    """
    base_slug = _slugify_text(title)
    if not base_slug:
        base_slug = "untitled"

    # Truncate to leave room for suffix
    base_slug = base_slug[:250]

    candidate = base_slug
    counter = 2

    while True:
        stmt = select(model_class.id).where(model_class.slug == candidate)
        if existing_id is not None:
            stmt = stmt.where(model_class.id != existing_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base_slug}-{counter}"
        counter += 1
