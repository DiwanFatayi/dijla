"""In-memory artifact store."""

from __future__ import annotations

from dijla.infrastructure.object_store import InMemoryArtifactStore


async def test_put_and_get() -> None:
    store = InMemoryArtifactStore()
    await store.ensure_buckets(["proofs"])
    uri = await store.put("proofs", "a.lean", b"by trivial")
    assert uri.startswith("mem://")
    assert (await store.get("proofs", "a.lean")) == b"by trivial"
