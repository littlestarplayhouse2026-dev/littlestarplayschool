"""Local file storage service for handling uploads."""

import hashlib
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.security import validate_file_signature
from app.models.stored_file import StoredFile

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


class LocalStorageService:
    """Handles saving, retrieving, and deleting uploaded files on the local filesystem."""

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
        """Save an uploaded file to disk and return a StoredFile metadata object.

        Steps:
        1. Validate extension
        2. Generate a safe storage key (UUID + extension)
        3. Stream file to disk, computing SHA-256 as we go
        4. Validate file signature (magic bytes)
        5. Build and return a StoredFile instance

        On any failure after the file has been written, the partially-written file is removed.
        """
        original_filename = file.filename or "unknown"
        extension = self._extract_extension(original_filename)

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

        file_id = uuid.uuid4()
        storage_key = f"{file_id}{extension}"
        dest_path = self.base_dir / storage_key

        sha256 = hashlib.sha256()
        file_size = 0
        first_chunk: bytes = b""

        try:
            async with aiofiles.open(dest_path, "wb") as out:
                while True:
                    chunk = await file.read(65_536)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > self.max_file_bytes:
                        raise ValueError(f"File exceeds the {self.max_file_bytes // (1024 * 1024)} MB size limit")
                    if not first_chunk:
                        first_chunk = chunk
                    sha256.update(chunk)
                    await out.write(chunk)

            # Validate magic bytes
            if file_size == 0:
                raise ValueError("Empty files cannot be uploaded")
            if not validate_file_signature(first_chunk, extension):
                dest_path.unlink(missing_ok=True)
                raise ValueError(
                    f"File content does not match the '{extension}' extension. "
                    "The file may be corrupted or incorrectly named."
                )

            mime_type = MIME_MAP.get(extension, "application/octet-stream")

            stored = StoredFile(
                id=file_id,
                storage_key=storage_key,
                original_filename=original_filename,
                display_filename=original_filename,
                mime_type=mime_type,
                extension=extension,
                file_size=file_size,
                sha256_checksum=sha256.hexdigest(),
                is_public=is_public,
                uploader_id=uploader_id,
            )
            return stored

        except Exception:
            # Clean up partial file on any error
            dest_path.unlink(missing_ok=True)
            raise

    async def get_file_path(self, storage_key: str) -> Path:
        """Return the full filesystem path for a stored file."""
        path = self.base_dir / storage_key
        if not path.exists():
            raise FileNotFoundError(f"File not found: {storage_key}")
        return path

    async def delete_file(self, storage_key: str) -> None:
        """Delete a file from disk by its storage key."""
        path = self.base_dir / storage_key
        path.unlink(missing_ok=True)

    @staticmethod
    def _extract_extension(filename: str) -> str:
        """Extract and lowercase the file extension, including the leading dot."""
        dot_idx = filename.rfind(".")
        if dot_idx == -1:
            return ""
        return filename[dot_idx:].lower()
