"""Local and Supabase object storage adapters for uploaded files."""

import asyncio
import hashlib
import logging
import uuid
from functools import lru_cache
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from app.core.config import settings
from app.core.security import validate_file_signature
from app.models.stored_file import StoredFile

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS: set[str] = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".pdf",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt",
}

MIME_MAP: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
}


class StorageError(RuntimeError):
    """Sanitized storage-provider failure safe to return from API handlers."""


def _validated_upload_metadata(file: UploadFile, content: bytes, max_file_bytes: int) -> tuple[str, str, str]:
    original_filename = file.filename or "unknown"
    extension = Path(original_filename.replace("\\", "/")).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{extension}' is not allowed. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if not content:
        raise ValueError("Empty files cannot be uploaded")
    if len(content) > max_file_bytes:
        raise ValueError(f"File exceeds the {max_file_bytes // (1024 * 1024)} MB size limit")

    supplied_mime = (file.content_type or "").split(";", 1)[0].strip().lower()
    expected_mime = MIME_MAP.get(extension)
    allowed_mime = {expected_mime, "application/octet-stream"}
    if extension in {".docx", ".xlsx", ".pptx"}:
        allowed_mime.update({"application/zip", "application/x-zip-compressed"})
    if supplied_mime and supplied_mime not in allowed_mime:
        raise ValueError("File MIME type does not match its extension")
    if not validate_file_signature(content[:65_536], extension):
        raise ValueError(
            f"File content does not match the '{extension}' extension. "
            "The file may be corrupted or incorrectly named."
        )
    return original_filename[:255], extension, MIME_MAP.get(extension, "application/octet-stream")


class LocalStorageService:
    """Handles development or explicitly persistent local filesystem storage."""

    backend = "local"

    def __init__(self, upload_dir: str, max_file_bytes: int = 10 * 1024 * 1024) -> None:
        self.base_dir = Path(upload_dir)
        self.max_file_bytes = max_file_bytes
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file: UploadFile,
        uploader_id: uuid.UUID | None = None,
        is_public: bool = False,
    ) -> StoredFile:
        """Validate and save an upload, returning its metadata row."""
        file_id = uuid.uuid4()
        original_filename = file.filename or "unknown"
        extension = Path(original_filename.replace("\\", "/")).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{extension}' is not allowed. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        supplied_mime = (file.content_type or "").split(";", 1)[0].strip().lower()
        expected_mime = MIME_MAP.get(extension)
        allowed_mime = {expected_mime, "application/octet-stream"}
        if extension in {".docx", ".xlsx", ".pptx"}:
            allowed_mime.update({"application/zip", "application/x-zip-compressed"})
        if supplied_mime and supplied_mime not in allowed_mime:
            raise ValueError("File MIME type does not match its extension")

        storage_key = f"{file_id}{extension}"
        dest_path = self.base_dir / storage_key
        sha256 = hashlib.sha256()
        file_size = 0
        first_chunk = b""
        try:
            async with aiofiles.open(dest_path, "wb") as out:
                while True:
                    chunk = await file.read(65_536)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > self.max_file_bytes:
                        raise ValueError(
                            f"File exceeds the {self.max_file_bytes // (1024 * 1024)} MB size limit"
                        )
                    if not first_chunk:
                        first_chunk = chunk
                    sha256.update(chunk)
                    await out.write(chunk)

            if file_size == 0:
                raise ValueError("Empty files cannot be uploaded")
            if not validate_file_signature(first_chunk, extension):
                raise ValueError(
                    f"File content does not match the '{extension}' extension. "
                    "The file may be corrupted or incorrectly named."
                )

            return StoredFile(
                id=file_id,
                storage_key=storage_key,
                storage_backend=self.backend,
                original_filename=original_filename[:255],
                display_filename=original_filename[:255],
                mime_type=MIME_MAP.get(extension, "application/octet-stream"),
                extension=extension,
                file_size=file_size,
                sha256_checksum=sha256.hexdigest(),
                is_public=is_public,
                uploader_id=uploader_id,
            )
        except Exception:
            dest_path.unlink(missing_ok=True)
            raise

    async def get_file_bytes(self, storage_key: str) -> bytes:
        """Read a stored object without accepting arbitrary filesystem paths."""
        if Path(storage_key).name != storage_key:
            raise FileNotFoundError("File not found")
        path = self.base_dir / storage_key
        try:
            async with aiofiles.open(path, "rb") as source:
                return await source.read()
        except FileNotFoundError:
            raise FileNotFoundError("File not found") from None

    async def delete_file(self, storage_key: str) -> None:
        """Delete a local object by its generated storage key."""
        if Path(storage_key).name != storage_key:
            raise ValueError("Invalid storage key")
        (self.base_dir / storage_key).unlink(missing_ok=True)


@lru_cache(maxsize=4)
def _supabase_client(url: str, service_role_key: str):
    """Reuse a backend-only Supabase client across requests in one process."""
    try:
        from supabase import create_client
    except ImportError:
        raise StorageError("Supabase Storage SDK is unavailable; install backend runtime dependencies") from None
    return create_client(url, service_role_key)


class SupabaseStorageService:
    """Private-bucket adapter; objects are served through the API's authorization checks."""

    backend = "supabase"

    def __init__(
        self,
        url: str | None = None,
        service_role_key: str | None = None,
        bucket: str | None = None,
        max_file_bytes: int = 10 * 1024 * 1024,
        client=None,
    ) -> None:
        self.url = url or settings.SUPABASE_URL
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
        self.max_file_bytes = max_file_bytes
        self._client_override = client

    @property
    def client(self):
        if self._client_override is not None:
            return self._client_override
        if not self.url or not self.service_role_key or not self.bucket:
            raise StorageError("Supabase Storage is not configured")
        try:
            return _supabase_client(self.url, self.service_role_key)
        except Exception:
            raise StorageError("Supabase Storage client could not be initialized") from None

    def _bucket(self):
        if not self.bucket:
            raise StorageError("Supabase Storage is not configured")
        return self.client.storage.from_(self.bucket)

    async def save_file(
        self,
        file: UploadFile,
        uploader_id: uuid.UUID | None = None,
        is_public: bool = False,
    ) -> StoredFile:
        """Validate and upload bytes under an unguessable, collision-resistant object path."""
        content = await file.read(self.max_file_bytes + 1)
        original_filename, extension, mime_type = _validated_upload_metadata(
            file, content, self.max_file_bytes
        )
        file_id = uuid.uuid4()
        storage_key = f"objects/{file_id.hex}/{file_id}{extension}"
        checksum = hashlib.sha256(content).hexdigest()
        try:
            bucket = self._bucket()
            await asyncio.to_thread(
                bucket.upload,
                path=storage_key,
                file=content,
                file_options={"content-type": mime_type, "upsert": "false"},
            )
        except Exception:
            raise StorageError("Persistent storage upload failed") from None

        return StoredFile(
            id=file_id,
            storage_key=storage_key,
            storage_backend=self.backend,
            original_filename=original_filename,
            display_filename=original_filename,
            mime_type=mime_type,
            extension=extension,
            file_size=len(content),
            sha256_checksum=checksum,
            is_public=is_public,
            uploader_id=uploader_id,
        )

    async def upload_existing_object(
        self,
        storage_key: str,
        content: bytes,
        content_type: str,
        *,
        upsert: bool = False,
    ) -> None:
        """Upload a legacy local object to its existing key for explicit migration."""
        if not _safe_object_key(storage_key):
            raise ValueError("Invalid storage key")
        try:
            bucket = self._bucket()
            await asyncio.to_thread(
                bucket.upload,
                path=storage_key,
                file=content,
                file_options={"content-type": content_type, "upsert": str(upsert).lower()},
            )
        except Exception:
            raise StorageError("Persistent storage upload failed") from None

    async def get_file_bytes(self, storage_key: str) -> bytes:
        """Download bytes from the private bucket after route-level authorization."""
        if not _safe_object_key(storage_key):
            raise FileNotFoundError("File not found")
        try:
            bucket = self._bucket()
            result = await asyncio.to_thread(bucket.download, storage_key)
        except Exception:
            raise StorageError("Persistent storage download failed") from None
        if not isinstance(result, bytes):
            raise StorageError("Persistent storage returned an invalid file response")
        return result

    async def delete_file(self, storage_key: str) -> None:
        """Delete a private-bucket object by its generated key."""
        if not _safe_object_key(storage_key):
            raise ValueError("Invalid storage key")
        try:
            bucket = self._bucket()
            await asyncio.to_thread(bucket.remove, [storage_key])
        except Exception:
            raise StorageError("Persistent storage deletion failed") from None


def _safe_object_key(storage_key: str) -> bool:
    """Only generated UUID object keys (and legacy local basenames) are accepted."""
    path = Path(storage_key)
    return bool(storage_key) and "\\" not in storage_key and ".." not in path.parts and not path.is_absolute()


def get_storage_service(backend: str | None = None):
    """Return the configured storage adapter for new uploads."""
    selected = (backend or settings.STORAGE_BACKEND).strip().lower()
    if selected == "supabase":
        return SupabaseStorageService(max_file_bytes=settings.max_upload_bytes)
    if selected == "local":
        return LocalStorageService(upload_dir=settings.UPLOAD_DIR, max_file_bytes=settings.max_upload_bytes)
    raise StorageError("Configured storage backend is not supported")


def get_storage_service_for_file(stored_file: StoredFile):
    """Resolve the adapter recorded on a metadata row, including legacy local rows."""
    return get_storage_service(getattr(stored_file, "storage_backend", "local"))
