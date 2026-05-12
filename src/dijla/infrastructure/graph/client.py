"""Memgraph client adapter.

Memgraph speaks the Bolt protocol, so we use the ``neo4j`` async driver. For
local development and tests we provide an in-memory implementation that
satisfies the read-only ``KnowledgeGraphReader`` protocol consumed by use
cases.
"""

from __future__ import annotations

import asyncio
from typing import Any

from dijla.core.logging import get_logger
from dijla.domain.entities import Certificate, Counterexample, Proof, Theorem

log = get_logger("dijla.graph")


class InMemoryKnowledgeGraph:
    """A tiny in-memory triple store with a Cypher-like read API."""

    def __init__(self) -> None:
        self._theorems: list[Theorem] = []
        self._proofs: list[Proof] = []
        self._certificates: list[Certificate] = []
        self._counterexamples: list[Counterexample] = []
        self._lock = asyncio.Lock()

    async def write_theorem(self, theorem: Theorem) -> None:
        async with self._lock:
            self._theorems.append(theorem)

    async def write_proof(self, proof: Proof) -> None:
        async with self._lock:
            self._proofs.append(proof)

    async def write_certificate(self, certificate: Certificate) -> None:
        async with self._lock:
            self._certificates.append(certificate)

    async def write_counterexample(self, counterexample: Counterexample) -> None:
        async with self._lock:
            self._counterexamples.append(counterexample)

    async def query(self, cypher: str) -> list[dict[str, object]]:
        """Tiny Cypher-shaped read API.

        Supported queries (case-insensitive):
          - ``MATCH (t:Theorem) RETURN t``
          - ``MATCH (p:Proof) RETURN p``
          - ``MATCH (c:Certificate) RETURN c``
          - ``MATCH (x:Counterexample) RETURN x``
        """
        upper = cypher.upper()
        if "THEOREM" in upper:
            return [t.model_dump(mode="json") for t in self._theorems]
        if "PROOF" in upper:
            return [p.model_dump(mode="json") for p in self._proofs]
        if "CERTIFICATE" in upper:
            return [c.model_dump(mode="json") for c in self._certificates]
        if "COUNTEREXAMPLE" in upper:
            return [c.model_dump(mode="json") for c in self._counterexamples]
        return []


class MemgraphClient:
    """Real Memgraph client using the neo4j Bolt async driver."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        username: str = "",
        password: str = "",
    ) -> None:
        self._uri = f"bolt://{host}:{port}"
        self._auth = (username, password) if username else None
        self._driver: Any | None = None

    async def connect(self) -> None:
        from neo4j import AsyncGraphDatabase

        self._driver = AsyncGraphDatabase.driver(self._uri, auth=self._auth)

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def write_theorem(self, theorem: Theorem) -> None:
        await self._run(
            "MERGE (t:Theorem {id: $id}) "
            "SET t.name = $name, t.status = $status, t.statement_lean = $statement_lean",
            id=theorem.id,
            name=theorem.name,
            status=theorem.status.value,
            statement_lean=theorem.statement_lean,
        )

    async def write_proof(self, proof: Proof) -> None:
        await self._run(
            "MATCH (t:Theorem {id: $theorem_id}) "
            "MERGE (p:Proof {id: $id}) "
            "SET p.term = $term, p.elapsed_ms = $elapsed_ms "
            "MERGE (t)-[:HAS_PROOF]->(p)",
            theorem_id=proof.theorem_id,
            id=proof.id,
            term=proof.term,
            elapsed_ms=proof.elapsed_ms,
        )

    async def write_certificate(self, certificate: Certificate) -> None:
        await self._run(
            "MERGE (c:Certificate {id: $id}) "
            "SET c.verifier = $verifier, c.verdict = $verdict, c.radius = $radius",
            id=certificate.id,
            verifier=certificate.verifier,
            verdict=certificate.verdict.value,
            radius=certificate.radius,
        )

    async def write_counterexample(self, counterexample: Counterexample) -> None:
        await self._run(
            "MATCH (t:Theorem {id: $theorem_id}) "
            "MERGE (x:Counterexample {id: $id}) "
            "MERGE (t)-[:REFUTED_BY]->(x)",
            theorem_id=counterexample.theorem_id,
            id=counterexample.id,
        )

    async def query(self, cypher: str) -> list[dict[str, object]]:
        if self._driver is None:
            await self.connect()
        assert self._driver is not None  # nosec
        async with self._driver.session() as session:
            result = await session.run(cypher)
            return [dict(record) async for record in result]

    async def _run(self, cypher: str, **params: object) -> None:
        if self._driver is None:
            await self.connect()
        assert self._driver is not None  # nosec
        async with self._driver.session() as session:
            await session.run(cypher, **params)
