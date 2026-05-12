"""In-process MCP clients — wrap the backend objects directly.

These are used by the orchestrator in the sandbox to avoid the cost of spawning
subprocesses for every tool call. They expose the same protocol surface as the
stdio clients.
"""

from __future__ import annotations

from dijla.mcp_servers.agnncert import AgnnCertBackend
from dijla.mcp_servers.lean4 import Lean4Backend
from dijla.mcp_servers.rcgnn import RcgnnBackend


class DirectLean4Client:
    def __init__(self, backend: Lean4Backend | None = None) -> None:
        self._backend = backend or Lean4Backend()

    async def check_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]:
        return await self._backend.check_tactic(theorem_name, tactic)

    async def apply_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]:
        return await self._backend.apply_tactic(theorem_name, tactic)

    async def verify_term(self, theorem_name: str, term: str) -> dict[str, object]:
        return await self._backend.verify_term(theorem_name, term)

    async def lean_search(self, query: str) -> dict[str, object]:
        return await self._backend.lean_search(query)


class DirectAgnnCertClient:
    def __init__(self, backend: AgnnCertBackend | None = None) -> None:
        self._backend = backend or AgnnCertBackend()

    async def certify_graph(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        return await self._backend.certify_graph(model, attack)

    async def certify_node(
        self,
        model: dict[str, object],
        attack: dict[str, object],
        node_id: int,
    ) -> dict[str, object]:
        return await self._backend.certify_node(model, attack, node_id)

    async def sample_attack(self, model: dict[str, object], seed: int) -> dict[str, object]:
        return await self._backend.sample_attack(model, seed)


class DirectRcgnnClient:
    def __init__(self, backend: RcgnnBackend | None = None) -> None:
        self._backend = backend or RcgnnBackend()

    async def certify_injection(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        return await self._backend.certify_injection(model, attack)

    async def compute_radius(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        return await self._backend.compute_radius(model, attack)
