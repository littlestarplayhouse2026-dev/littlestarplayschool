"""CLI utility to create initial administrator users."""

import asyncio
import hashlib
import getpass
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.user import User
from app.models.stored_file import StoredFile
from app.core.config import settings
from app.services.storage_service import LocalStorageService, StorageError, SupabaseStorageService


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


async def migrate_local_files_to_supabase() -> None:
    """Copy legacy local objects to Supabase, then mark each DB record migrated."""
    if settings.STORAGE_BACKEND != "supabase":
        print("Error: Set STORAGE_BACKEND=supabase before running this migration.")
        sys.exit(1)
    if not Path(settings.UPLOAD_DIR).is_dir():
        print("Error: UPLOAD_DIR is not present; refusing to migrate without the original local files.")
        sys.exit(1)
    local = LocalStorageService(settings.UPLOAD_DIR, settings.max_upload_bytes)
    remote = SupabaseStorageService(max_file_bytes=settings.max_upload_bytes)
    migrated = 0
    async with async_session_factory() as db:
        rows = (await db.execute(select(StoredFile).where(StoredFile.storage_backend == "local"))).scalars().all()
        for row in rows:
            try:
                content = await local.get_file_bytes(row.storage_key)
                if len(content) != row.file_size or hashlib.sha256(content).hexdigest() != row.sha256_checksum:
                    raise ValueError("local file size or checksum does not match database metadata")
                await remote.upload_existing_object(row.storage_key, content, row.mime_type, upsert=True)
                row.storage_backend = "supabase"
                await db.commit()
                migrated += 1
            except (OSError, ValueError, StorageError):
                await db.rollback()
                print(f"Migration stopped at file {row.id}; local file was retained. Check storage connectivity and metadata.")
                sys.exit(1)
    print(f"Migrated {migrated} file(s). Local originals were retained.")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "create-admin":
        asyncio.run(create_admin_interactive())
    elif len(sys.argv) > 1 and sys.argv[1] == "migrate-local-files-to-supabase":
        asyncio.run(migrate_local_files_to_supabase())
    else:
        print("Usage: python -m app.cli {create-admin|migrate-local-files-to-supabase}")


if __name__ == "__main__":
    main()

