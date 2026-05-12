"""Object-store adapters: MinIO + in-memory fallback."""

from dijla.infrastructure.object_store.client import InMemoryArtifactStore, MinioArtifactStore

__all__ = ["InMemoryArtifactStore", "MinioArtifactStore"]
