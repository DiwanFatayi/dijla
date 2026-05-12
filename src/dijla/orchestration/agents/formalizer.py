"""Formalizer agent — produces Lean 4 statements from natural-language hypotheses.

Real backend: **Aria** with Graph-of-Thought + AriaScorer. The sandbox mock
emits syntactically valid Lean 4 stubs (the verifier MCP catches semantic
errors downstream — the Formalizer's job is only to provide a starting point).
"""

from __future__ import annotations

import re

from dijla.domain.entities import Hypothesis, Theorem
from dijla.orchestration.state import ScientificState


class FormalizerAgent:
    """Templated, deterministic formalization."""

    name = "formalizer"

    async def __call__(self, state: ScientificState) -> dict[str, object]:
        statement_lean = self._formalize(state.hypothesis)
        theorem_name = self._slug(state.hypothesis.title)
        theorem = Theorem(
            hypothesis_id=state.hypothesis.id,
            name=theorem_name,
            statement_lean=statement_lean,
        )
        trace = [*state.trace, f"formalizer produced theorem `{theorem_name}`"]
        return {
            "formal_statement": statement_lean,
            "theorem": theorem,
            "trace": trace,
        }

    @staticmethod
    def _slug(title: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", title.strip())
        slug = slug.strip("_").lower() or "anon_theorem"
        # Lean identifiers can't start with a digit
        if slug[0].isdigit():
            slug = f"t_{slug}"
        return slug

    @staticmethod
    def _formalize(hypothesis: Hypothesis) -> str:
        slug = FormalizerAgent._slug(hypothesis.title)
        body = hypothesis.statement.replace("`", "'").replace("\n", " ")
        return (
            f"-- {body}\n"
            f"theorem {slug} (G : Graph) (N : GNN) (a : Attack) :\n"
            f"  Robust G N a := by\n"
            f"  sorry\n"
        )
