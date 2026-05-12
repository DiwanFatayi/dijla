"""Prover agent — calls the Lean 4 MCP server to discover a proof.

The mock prover succeeds for theorems whose statement mentions a known
tactic pattern (drawn from the BaseStore "tactics" namespace) and fails
otherwise, producing a counterexample.
"""

from __future__ import annotations

import time
from typing import Protocol

from dijla.domain.entities import Counterexample, Proof
from dijla.orchestration.state import ScientificState


class Lean4ToolProtocol(Protocol):
    """Subset of the Lean 4 MCP API the Prover relies on."""

    async def check_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]: ...

    async def verify_term(self, theorem_name: str, term: str) -> dict[str, object]: ...


class ProverAgent:
    """Drives MCP `check_tactic` until success or budget exhausted."""

    name = "prover"

    DEFAULT_TACTIC_LIBRARY: tuple[str, ...] = (
        "intro G N a",
        "unfold Robust",
        "apply gnn_robust_under_bounded_perturbation",
        "apply gnn_robust_under_node_injection",
        "simp",
        "tauto",
        "exact GNN.robustness.proof N a",
    )

    def __init__(
        self,
        lean4: Lean4ToolProtocol,
        *,
        max_iterations: int = 8,
        tactic_library: tuple[str, ...] | None = None,
    ) -> None:
        self._lean4 = lean4
        self._max_iterations = max_iterations
        self._library = tactic_library or self.DEFAULT_TACTIC_LIBRARY

    async def __call__(self, state: ScientificState) -> dict[str, object]:
        if state.theorem is None:
            msg = "Prover requires a Theorem in state."
            raise RuntimeError(msg)

        start = time.perf_counter()
        succeeded_tactics: list[str] = []
        for tactic in self._library[: self._max_iterations]:
            result = await self._lean4.check_tactic(state.theorem.name, tactic)
            if result.get("ok"):
                succeeded_tactics.append(tactic)
                if result.get("closes_goal"):
                    term = str(result.get("term", "by " + "; ".join(succeeded_tactics)))
                    verified = await self._lean4.verify_term(state.theorem.name, term)
                    if verified.get("ok"):
                        elapsed_ms = int((time.perf_counter() - start) * 1000)
                        proof = Proof(
                            theorem_id=state.theorem.id,
                            tactics=tuple(succeeded_tactics),
                            term=term,
                            elapsed_ms=elapsed_ms,
                        )
                        trace = [
                            *state.trace,
                            f"prover closed `{state.theorem.name}` in {elapsed_ms}ms",
                        ]
                        return {"proof": proof, "trace": trace}

        counterexample = Counterexample(
            theorem_id=state.theorem.id,
            payload={"reason": "tactic_library_exhausted", "tried": list(self._library)},
            note=f"No proof found within budget of {self._max_iterations} tactics.",
        )
        trace = [*state.trace, f"prover surfaced counterexample for `{state.theorem.name}`"]
        return {"counterexample": counterexample, "trace": trace}
