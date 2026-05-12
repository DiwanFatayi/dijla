"""Long-term cross-session memory using LangGraph BaseStore.

In the PoC, we wrap an in-memory ``InMemoryStore`` so the orchestrator code
treats memory uniformly. Production deploys swap in ``AsyncPostgresStore``.
"""

from __future__ import annotations

from typing import Any

from langgraph.store.memory import InMemoryStore


class LongTermMemoryStore:
    """Thin wrapper around a LangGraph BaseStore."""

    def __init__(self, store: Any | None = None) -> None:
        self._store = store or InMemoryStore()

    @property
    def raw(self) -> Any:
        return self._store

    async def remember_tactic(self, theorem_name: str, tactic: str) -> None:
        await self._store.aput(("tactics",), theorem_name, {"tactic": tactic})

    async def recall_tactics(self) -> list[dict[str, object]]:
        items = await self._store.asearch(("tactics",))
        return [{"key": item.key, **item.value} for item in items]

    async def remember_counterexample(self, theorem_name: str, payload: dict[str, object]) -> None:
        await self._store.aput(("counterexamples",), theorem_name, payload)

    async def recall_counterexamples(self) -> list[dict[str, object]]:
        items = await self._store.asearch(("counterexamples",))
        return [{"key": item.key, **item.value} for item in items]
