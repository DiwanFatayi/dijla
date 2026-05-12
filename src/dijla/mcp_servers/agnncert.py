"""AGNNCert MCP server.

PoC backend implements the certificate algebra deterministically. Production
swaps in the real AGNNCert wheel.
"""

from __future__ import annotations

import asyncio
import math
from typing import Any

from dijla.core.logging import get_logger
from dijla.mcp_servers._common import stable_hash

log = get_logger("dijla.mcp.agnncert")


class AgnnCertBackend:
    """Closed-form deterministic certificate bound."""

    async def certify_graph(
        self,
        model: dict[str, object],
        attack: dict[str, object],
    ) -> dict[str, object]:
        await asyncio.sleep(0)
        layers_raw = model.get("layers", 3)
        budget_raw = attack.get("budget", 1)
        layers = int(layers_raw) if isinstance(layers_raw, (int, float, str)) else 3
        budget = int(budget_raw) if isinstance(budget_raw, (int, float, str)) else 1
        # Sound (mock) bound: radius = log(1 + 1/budget) / layers, with hard
        # floor for "REFUTED" when budget exceeds a threshold and layers is small.
        if budget > 64 and layers < 4:
            verdict = "refuted"
            radius = 0.0
        else:
            radius = math.log(1.0 + 1.0 / max(budget, 1)) / layers
            verdict = "proved" if radius > 0.05 else "open"
        artefact_uri = f"mock://agnncert/{stable_hash(model, attack)}"
        return {
            "verdict": verdict,
            "radius": round(radius, 6),
            "artifact_uri": artefact_uri,
            "verifier": "agnncert",
        }

    async def certify_node(
        self,
        model: dict[str, object],
        attack: dict[str, object],
        node_id: int,
    ) -> dict[str, object]:
        result = await self.certify_graph(model, attack)
        result["node_id"] = node_id
        return result

    async def sample_attack(self, model: dict[str, object], seed: int) -> dict[str, object]:
        await asyncio.sleep(0)
        budget = (seed % 16) + 1
        return {
            "kind": "edge_perturbation",
            "budget": budget,
            "trace_id": stable_hash(model, seed),
        }


def _build_fastmcp() -> Any:
    from mcp.server.fastmcp import FastMCP

    backend = AgnnCertBackend()
    server: Any = FastMCP("dijla-agnncert")

    @server.tool()  # type: ignore[untyped-decorator]
    async def certify_graph(
        model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        """Run AGNNCert on a (model, attack) pair."""
        return await backend.certify_graph(model, attack)

    @server.tool()  # type: ignore[untyped-decorator]
    async def certify_node(
        model: dict[str, object], attack: dict[str, object], node_id: int
    ) -> dict[str, object]:
        """Certify a single node against the attack."""
        return await backend.certify_node(model, attack, node_id)

    @server.tool()  # type: ignore[untyped-decorator]
    async def sample_attack(model: dict[str, object], seed: int) -> dict[str, object]:
        """Sample a candidate adversarial attack for the model."""
        return await backend.sample_attack(model, seed)

    return server


def run() -> None:  # pragma: no cover
    _build_fastmcp().run()


if __name__ == "__main__":  # pragma: no cover
    run()
