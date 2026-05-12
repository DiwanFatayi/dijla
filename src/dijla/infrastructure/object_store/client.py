"""Artifact storage abstraction (MinIO + in-memory)."""

from __future__ import annotations

import asyncio
from typing import Protocol


class ArtifactStore(Protocol):
    async def put(self, bucket: str, key: str, data: bytes) -> str: ...
    async def get(self, bucket: str, key: str) -> bytes: ...
    async def ensure_buckets(self, buckets: list[str]) -> None: ...


class InMemoryArtifactStore:
    """In-memory artifact store used in tests and the default PoC config."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], bytes] = {}
        self._buckets: set[str] = set()
        self._lock = asyncio.Lock()

    async def put(self, bucket: str, key: str, data: bytes) -> str:
        async with self._lock:
            self._buckets.add(bucket)
            self._store[(bucket, key)] = data
        return f"mem://{bucket}/{key}"

    async def get(self, bucket: str, key: str) -> bytes:
        return self._store[(bucket, key)]

    async def ensure_buckets(self, buckets: list[str]) -> None:
        async with self._lock:
            self._buckets.update(buckets)


class MinioArtifactStore:
    """Async-friendly wrapper around the synchronous MinIO Python SDK."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        *,
        secure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._secure = secure
        self._client: object | None = None

    def _ensure_client(self) -> object:
        if self._client is None:
            from minio import Minio

            self._client = Minio(
                self._endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key,
                secure=self._secure,
            )
        return self._client

    async def ensure_buckets(self, buckets: list[str]) -> None:
        def _do() -> None:
            client = self._ensure_client()
            for bucket in buckets:
                if not client.bucket_exists(bucket):  # type: ignore[attr-defined]
                    client.make_bucket(bucket)  # type: ignore[attr-defined]

        await asyncio.to_thread(_do)

    async def put(self, bucket: str, key: str, data: bytes) -> str:
        import io

        def _do() -> None:
            client = self._ensure_client()
            client.put_object(  # type: ignore[attr-defined]
                bucket,
                key,
                io.BytesIO(data),
                length=len(data),
                content_type="application/octet-stream",
            )

        await asyncio.to_thread(_do)
        return f"s3://{bucket}/{key}"

    async def get(self, bucket: str, key: str) -> bytes:
        def _do() -> bytes:
            client = self._ensure_client()
            response = client.get_object(bucket, key)  # type: ignore[attr-defined]
            try:
                return bytes(response.read())
            finally:
                response.close()
                response.release_conn()

        return await asyncio.to_thread(_do)
