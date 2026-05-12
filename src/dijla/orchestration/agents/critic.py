"""Critic agent — produces commentary and next-step hints."""

from __future__ import annotations

from dijla.orchestration.state import ScientificState


class CriticAgent:
    """Generates a short critique of the cycle outcome."""

    name = "critic"

    async def __call__(self, state: ScientificState) -> dict[str, object]:
        if state.counterexample is not None:
            critique = (
                f"Cycle refuted: `{state.theorem.name if state.theorem else 'unknown'}`. "
                "Re-enqueue weaker hypothesis or strengthen tactic library."
            )
        elif state.proof is not None and state.certificate is not None:
            critique = (
                f"Cycle succeeded: proof verified, headline certificate radius="
                f"{state.certificate.radius:.4f} verdict={state.certificate.verdict.value}. "
                "Add proof tactics to BaseStore tactics namespace."
            )
        else:
            critique = "Cycle produced no actionable artefact; inspect trace."
        trace = [*state.trace, f"critic: {critique}"]
        return {"critique": critique, "trace": trace}
