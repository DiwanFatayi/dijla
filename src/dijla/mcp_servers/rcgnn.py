"""RCGNN MCP server (node-injection certification)."""

from __future__ import annotations

import asyncio
import math
from typing import Any

from dijla.core.logging import get_logger
from dijla.mcp_servers._common import stable_hash

log = get_logger("dijla.mcp.rcgnn")


class RcgnnBackend:
    """RCGNN deterministic bound for node-injection robustness."""

    async def certify_injection(
        self,
        model: dict[str, object],
        attack: dict[str, object],
    ) -> dict[str, object]:
        await asyncio.sleep(0)
        layers_raw = model.get("layers", 3)
        budget_raw = attack.get("budget", 1)
        layers = int(layers_raw) if isinstance(layers_raw, (int, float, str)) else 3
        budget = int(budget_raw) if isinstance(budget_raw, (int, float, str)) else 1
        radius = math.exp(-budget / (layers + 1.0))
        if budget > 128:
            verdict = "refuted"
            radius = 0.0
        elif radius > 0.05:
            verdict = "proved"
        else:
            verdict = "open"
        return {
            "verdict": verdict,
            "radius": round(radius, 6),
            "artifact_uri": f"mock://rcgnn/{stable_hash(model, attack)}",
            "verifier": "rcgnn",
        }

    async def compute_radius(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        result = await self.certify_injection(model, attack)
        return {"radius": result["radius"]}


def _build_fastmcp() -> Any:
    from mcp.server.fastmcp import FastMCP

    backend = RcgnnBackend()
    server: Any = FastMCP("dijla-rcgnn")

    @server.tool()  # type: ignore[untyped-decorator]
    async def certify_injection(
        model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        """Certify a GNN against a node-injection attack."""
        return await backend.certify_injection(model, attack)

    @server.tool()  # type: ignore[untyped-decorator]
    async def compute_radius(
        model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        """Return the certified radius only."""
        return await backend.compute_radius(model, attack)

    return server


def run() -> None:  # pragma: no cover
    _build_fastmcp().run()


if __name__ == "__main__":  # pragma: no cover
    run()
