"""CLI utility to create initial administrator users."""

import asyncio
import getpass
import sys
from uuid import uuid4

from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.user import User


async def create_admin_interactive() -> None:
    """Prompt for user details and create an administrator in the database."""
    print("=== Little Star Playhouse — Create Administrator ===")

    username = input("Admin Username: ").strip()
    if not username:
        print("Error: A username is required.")
        sys.exit(1)

    display_name = input("Display Name [Playhouse Administrator]: ").strip()
    if not display_name:
        display_name = "Playhouse Administrator"

    password = getpass.getpass("Password: ")
    if len(password) < 12:
        print("Error: Password must be at least 12 characters.")
        sys.exit(1)

    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("Error: Passwords do not match.")
        sys.exit(1)

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(func.lower(User.username) == username.lower()))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Error: A user with username '{username}' already exists.")
            sys.exit(1)

        new_user = User(
            id=uuid4(),
            username=username,
            password_hash=hash_password(password),
            display_name=display_name,
            role="ADMIN",
            is_active=True,
        )
        db.add(new_user)
        await db.commit()
        print(f"\nSuccess! Administrator '{display_name}' ({username}) created successfully.")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "create-admin":
        asyncio.run(create_admin_interactive())
    else:
        print("Usage: python -m app.cli create-admin")


if __name__ == "__main__":
    main()

