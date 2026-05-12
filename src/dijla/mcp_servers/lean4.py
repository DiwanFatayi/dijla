"""Lean 4 MCP server.

The PoC backend is a deterministic tactic interpreter. Tactics that match a
curated allow-list either close the goal or report progress; unknown tactics
return an error. In production this backend is replaced by a LeanDojo-driven
sandbox running ``lake env lean`` against mathlib4.
"""

from __future__ import annotations

import asyncio
from typing import Any

from dijla.core.logging import get_logger
from dijla.mcp_servers._common import stable_hash

log = get_logger("dijla.mcp.lean4")

# Tactics that close the goal in the mock interpreter
_CLOSING_TACTICS: frozenset[str] = frozenset(
    {
        "exact GNN.robustness.proof N a",
        "apply gnn_robust_under_bounded_perturbation",
        "apply gnn_robust_under_node_injection",
        "tauto",
    }
)

# Tactics that make progress without closing
_PROGRESS_TACTICS: frozenset[str] = frozenset(
    {
        "intro G N a",
        "unfold Robust",
        "simp",
        "rfl",
        "constructor",
    }
)


class Lean4Backend:
    """Pure-Python implementation of the Lean 4 MCP tools."""

    async def check_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]:
        await asyncio.sleep(0)
        if tactic in _CLOSING_TACTICS:
            term = f"by {tactic}"
            return {
                "ok": True,
                "closes_goal": True,
                "term": term,
                "trace_id": stable_hash(theorem_name, tactic, "close"),
            }
        if tactic in _PROGRESS_TACTICS:
            return {
                "ok": True,
                "closes_goal": False,
                "trace_id": stable_hash(theorem_name, tactic, "progress"),
            }
        return {
            "ok": False,
            "error": f"unknown tactic: {tactic!r}",
            "trace_id": stable_hash(theorem_name, tactic, "error"),
        }

    async def apply_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]:
        return await self.check_tactic(theorem_name, tactic)

    async def verify_term(self, theorem_name: str, term: str) -> dict[str, object]:
        await asyncio.sleep(0)
        ok = term.startswith("by ")
        return {
            "ok": ok,
            "theorem": theorem_name,
            "term": term,
            "trace_id": stable_hash(theorem_name, term, "verify"),
        }

    async def lean_search(self, query: str) -> dict[str, object]:
        await asyncio.sleep(0)
        suggestions = [t for t in (*_CLOSING_TACTICS, *_PROGRESS_TACTICS) if query.lower() in t]
        return {"query": query, "suggestions": sorted(suggestions)}


def _build_fastmcp() -> Any:
    """Build a FastMCP server exposing the backend tools."""
    from mcp.server.fastmcp import FastMCP

    backend = Lean4Backend()
    server: Any = FastMCP("dijla-lean4")

    @server.tool()  # type: ignore[untyped-decorator]
    async def check_tactic(theorem_name: str, tactic: str) -> dict[str, object]:
        """Apply a single Lean 4 tactic and report whether it closes the goal."""
        return await backend.check_tactic(theorem_name, tactic)

    @server.tool()  # type: ignore[untyped-decorator]
    async def apply_tactic(theorem_name: str, tactic: str) -> dict[str, object]:
        """Apply a tactic (alias for check_tactic for now)."""
        return await backend.apply_tactic(theorem_name, tactic)

    @server.tool()  # type: ignore[untyped-decorator]
    async def verify_term(theorem_name: str, term: str) -> dict[str, object]:
        """Verify a final Lean 4 proof term against the goal."""
        return await backend.verify_term(theorem_name, term)

    @server.tool()  # type: ignore[untyped-decorator]
    async def lean_search(query: str) -> dict[str, object]:
        """Search the known tactic library."""
        return await backend.lean_search(query)

    return server


def run() -> None:  # pragma: no cover - subprocess entrypoint
    """Console-script entry point that runs the stdio server."""
    server = _build_fastmcp()
    server.run()


if __name__ == "__main__":  # pragma: no cover
    run()
