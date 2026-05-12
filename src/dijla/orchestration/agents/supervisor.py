"""Supervisor agent — deterministic router.

Production swaps this out for a Claude Opus 4.7 client that returns the same
`AgentRoute`. The deterministic policy below is the *contract* the LLM is
expected to honour.
"""

from __future__ import annotations

from dijla.orchestration.state import AgentRoute, ScientificState


class SupervisorAgent:
    """Decides the next route based on accumulated state."""

    name = "supervisor"

    def __init__(self, *, require_human: bool = True) -> None:
        self._require_human = require_human

    async def __call__(self, state: ScientificState) -> dict[str, object]:
        route = self._route(state)
        trace = [*state.trace, f"supervisor → {route.value}"]
        return {"next_step": route, "trace": trace}

    def _route(self, state: ScientificState) -> AgentRoute:
        if state.formal_statement is None:
            return AgentRoute.FORMALIZE
        if state.theorem is None and self._require_human and state.human_decision_formal is None:
            return AgentRoute.HUMAN_APPROVAL_FORMAL
        if state.proof is None and state.counterexample is None:
            return AgentRoute.PROVE
        if state.counterexample is not None and state.critique is None:
            return AgentRoute.CRITIQUE
        if state.proof is not None and state.certificate is None:
            return AgentRoute.VERIFY
        if (
            state.proof is not None
            and state.certificate is not None
            and self._require_human
            and state.human_decision_commit is None
        ):
            return AgentRoute.HUMAN_APPROVAL_COMMIT
        if state.critique is None and state.proof is not None:
            return AgentRoute.CRITIQUE
        return AgentRoute.FINALIZE
