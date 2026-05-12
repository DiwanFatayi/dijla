"""Long-term memory and checkpointer tests."""

from __future__ import annotations

import pytest

from dijla.orchestration.memory import LongTermMemoryStore, build_checkpointer


async def test_memory_store_remembers_tactics() -> None:
    store = LongTermMemoryStore()
    await store.remember_tactic("t1", "exact h")
    items = await store.recall_tactics()
    assert any(item["tactic"] == "exact h" for item in items)


async def test_memory_store_remembers_counterexamples() -> None:
    store = LongTermMemoryStore()
    await store.remember_counterexample("t2", {"graph": "k_5"})
    items = await store.recall_counterexamples()
    assert any(item["graph"] == "k_5" for item in items)


def test_build_checkpointer_memory() -> None:
    cp = build_checkpointer("memory")
    assert cp is not None


def test_build_checkpointer_invalid() -> None:
    with pytest.raises(ValueError, match="Unknown checkpointer backend"):
        build_checkpointer("nope")  # type: ignore[arg-type]


def test_build_checkpointer_sqlite_requires_dsn() -> None:
    with pytest.raises(ValueError, match="requires `dsn`"):
        build_checkpointer("sqlite")


def test_build_checkpointer_postgres_requires_dsn() -> None:
    with pytest.raises(ValueError, match="requires `dsn`"):
        build_checkpointer("postgres")
