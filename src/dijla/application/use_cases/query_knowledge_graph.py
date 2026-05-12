"""Query the knowledge graph (Memgraph)."""

from __future__ import annotations

from typing import Protocol


class KnowledgeGraphReader(Protocol):
    async def query(self, cypher: str) -> list[dict[str, object]]: ...


class QueryKnowledgeGraphUseCase:
    def __init__(self, reader: KnowledgeGraphReader) -> None:
        self._reader = reader

    async def execute(self, cypher: str) -> list[dict[str, object]]:
        upper = cypher.strip().upper()
        for forbidden in ("CREATE ", "MERGE ", "DELETE ", "SET ", "REMOVE "):
            if forbidden in upper:
                msg = f"Read-only query violated: contains `{forbidden.strip()}`."
                raise ValueError(msg)
        return await self._reader.query(cypher)
