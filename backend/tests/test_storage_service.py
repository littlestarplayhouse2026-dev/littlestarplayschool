import hashlib
import tempfile
from types import SimpleNamespace

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.storage_service import StorageError, SupabaseStorageService
import app.services.storage_service as storage_module


def upload_file(data: bytes, filename: str) -> UploadFile:
    file = tempfile.SpooledTemporaryFile()
    file.write(data)
    file.seek(0)
    return UploadFile(filename=filename, file=file, headers=Headers({"content-type": "text/plain"}))


class FakeBucket:
    def __init__(self):
        self.objects = {}

    def upload(self, path, file, file_options):
        if path in self.objects and file_options.get("upsert") != "true":
            raise RuntimeError("duplicate object")
        self.objects[path] = bytes(file)

    def download(self, path):
        return self.objects[path]

    def remove(self, paths):
        for path in paths:
            self.objects.pop(path, None)


class FakeClient:
    def __init__(self):
        self.bucket = FakeBucket()
        self.storage = SimpleNamespace(from_=lambda _name: self.bucket)


@pytest.mark.asyncio
async def test_supabase_storage_saves_downloads_and_deletes_with_private_object_key(monkeypatch):
    async def run_inline(function, *args, **kwargs):
        return function(*args, **kwargs)
    monkeypatch.setattr(storage_module.asyncio, "to_thread", run_inline)
    client = FakeClient()
    storage = SupabaseStorageService(client=client, bucket="private", max_file_bytes=100)
    file = upload_file(b"A production note", "note.txt")
    record = await storage.save_file(file, is_public=False)
    assert record.storage_backend == "supabase"
    assert record.storage_key.startswith("objects/")
    assert record.sha256_checksum == hashlib.sha256(b"A production note").hexdigest()
    assert await storage.get_file_bytes(record.storage_key) == b"A production note"
    await storage.delete_file(record.storage_key)
    assert record.storage_key not in client.bucket.objects


@pytest.mark.asyncio
async def test_supabase_storage_sanitizes_provider_errors(monkeypatch):
    async def run_inline(function, *args, **kwargs):
        return function(*args, **kwargs)
    monkeypatch.setattr(storage_module.asyncio, "to_thread", run_inline)
    class BrokenBucket(FakeBucket):
        def upload(self, path, file, file_options):
            raise RuntimeError("secret-token-must-not-escape")

    client = FakeClient()
    client.bucket = BrokenBucket()
    client.storage = SimpleNamespace(from_=lambda _name: client.bucket)
    storage = SupabaseStorageService(client=client, bucket="private")
    file = upload_file(b"hello", "note.txt")
    with pytest.raises(StorageError) as exc:
        await storage.save_file(file)
    assert "secret-token" not in str(exc.value)
