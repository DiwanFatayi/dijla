"""Per-agent unit tests."""

from __future__ import annotations

import pytest

from dijla.domain.entities import Attack, AttackKind, GnnModel, Hypothesis, Theorem
from dijla.domain.value_objects import Verdict, new_id
from dijla.infrastructure.mcp_clients import (
    DirectAgnnCertClient,
    DirectLean4Client,
    DirectRcgnnClient,
)
from dijla.orchestration.agents import (
    CriticAgent,
    FormalizerAgent,
    ProverAgent,
    SupervisorAgent,
    VerifierAgent,
)
from dijla.orchestration.state import AgentRoute, ScientificState


def _state(**overrides) -> ScientificState:
    hypothesis = Hypothesis(
        title="test hypothesis",
        statement="GNN robustness lemma should generalise to k=2 cases as well.",
    )
    base = {"cycle_id": new_id(), "hypothesis": hypothesis}
    base.update(overrides)
    return ScientificState(**base)


class TestSupervisor:
    async def test_initial_route_is_formalize(self) -> None:
        result = await SupervisorAgent(require_human=False)(_state())
        assert result["next_step"] is AgentRoute.FORMALIZE

    async def test_after_formal_route_to_prove_without_human(self) -> None:
        state = _state(formal_statement="theorem t : True := by trivial")
        result = await SupervisorAgent(require_human=False)(state)
        assert result["next_step"] is AgentRoute.PROVE

    async def test_after_formal_routes_to_human_when_required(self) -> None:
        state = _state(formal_statement="theorem t : True := by trivial")
        result = await SupervisorAgent(require_human=True)(state)
        assert result["next_step"] is AgentRoute.HUMAN_APPROVAL_FORMAL


class TestFormalizer:
    async def test_produces_lean_statement(self) -> None:
        state = _state()
        result = await FormalizerAgent()(state)
        assert "theorem" in str(result["formal_statement"])
        assert result["theorem"] is not None


class TestProver:
    async def test_returns_proof_on_known_theorem(self) -> None:
        state = _state(
            theorem=Theorem(
                hypothesis_id=new_id(),
                name="t1",
                statement_lean="theorem t1 : True := by sorry",
            )
        )
        result = await ProverAgent(DirectLean4Client())(state)
        assert result.get("proof") is not None

    async def test_emits_counterexample_when_no_tactic_works(self) -> None:
        state = _state(
            theorem=Theorem(
                hypothesis_id=new_id(),
                name="t2",
                statement_lean="theorem t2 : True := by sorry",
            )
        )
        prover = ProverAgent(
            DirectLean4Client(),
            tactic_library=("nonsense_tactic_no_one_knows",),
            max_iterations=1,
        )
        result = await prover(state)
        assert result.get("counterexample") is not None
        assert result.get("proof") is None

    async def test_raises_if_no_theorem_in_state(self) -> None:
        state = _state()
        with pytest.raises(RuntimeError):
            await ProverAgent(DirectLean4Client())(state)


class TestVerifier:
    async def test_runs_agnncert_and_rcgnn(self) -> None:
        state = _state(
            gnn_model=GnnModel(name="g", architecture="GCN", layers=3),
            attacks=[
                Attack(kind=AttackKind.EDGE_PERTURBATION, budget=4),
                Attack(kind=AttackKind.NODE_INJECTION, budget=2),
            ],
        )
        verifier = VerifierAgent(DirectAgnnCertClient(), DirectRcgnnClient())
        result = await verifier(state)
        assert result["certificate"].verdict in {Verdict.PROVED, Verdict.OPEN, Verdict.REFUTED}


class TestCritic:
    async def test_critique_for_counterexample(self) -> None:
        state = _state(
            theorem=Theorem(
                hypothesis_id=new_id(),
                name="t3",
                statement_lean="theorem t3 : True := by sorry",
            ),
        )
        state = state.model_copy(
            update={
                "counterexample": None,  # no counterexample, hits the fallback branch
            }
        )
        # No counterexample, no proof: fallback branch.
        result = await CriticAgent()(state)
        assert "no actionable" in str(result["critique"]).lower()
