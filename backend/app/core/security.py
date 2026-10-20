"""Security utilities: password hashing, session tokens, sanitization, file validation."""

import hashlib
import secrets

import bleach
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


_password_hash = PasswordHash((Argon2Hasher(),))

# Allowed HTML tags and attributes for notice body sanitization
_ALLOWED_TAGS = [
    "p", "br", "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "u", "a", "ul", "ol", "li",
    "blockquote", "img",
]

_ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "class"],
    "img": ["src", "alt", "class"],
}

# Magic-byte signatures for file validation
_FILE_SIGNATURES: dict[str, list[bytes]] = {
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".png": [b"\x89PNG"],  # 89504E47
    ".pdf": [b"%PDF"],  # 25504446
    ".webp": [b"RIFF"],  # 52494646 — full check includes WEBP at offset 8
    ".docx": [b"PK\x03\x04"],  # 504B0304
    ".xlsx": [b"PK\x03\x04"],
    ".pptx": [b"PK\x03\x04"],
    ".doc": [b"\xd0\xcf\x11\xe0"],  # OLE2
    ".xls": [b"\xd0\xcf\x11\xe0"],
    ".ppt": [b"\xd0\xcf\x11\xe0"],
}


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against its Argon2 hash."""
    return _password_hash.verify(password, hashed)


def generate_session_token() -> str:
    """Generate a cryptographically random session token."""
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    """SHA-256 hash a session token for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_csrf_token() -> str:
    """Generate a cryptographically random CSRF token."""
    return secrets.token_urlsafe(32)


def sanitize_html(html: str) -> str:
    """Sanitize user-provided HTML, allowing only safe tags and attributes."""
    return bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
    )


def validate_file_signature(file_bytes: bytes, extension: str) -> bool:
    """Validate that the first bytes of a file match expected magic bytes for its extension.

    Returns True if the extension is not in the signature map (e.g. .txt) or
    if the magic bytes match. Returns False only when we have a known signature
    and the file does NOT match.
    """
    ext = extension.lower()
    signatures = _FILE_SIGNATURES.get(ext)
    if signatures is None:
        # No known signature to validate — allow by default
        return True

    for sig in signatures:
        if file_bytes[: len(sig)] == sig:
            # Extra check for WebP: bytes 8-12 should be "WEBP"
            if ext == ".webp":
                return len(file_bytes) >= 12 and file_bytes[8:12] == b"WEBP"
            return True
    return False
