"""Tests for domain entities."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from dijla.domain.entities import (
    Attack,
    AttackKind,
    Certificate,
    Counterexample,
    Cycle,
    Event,
    EventKind,
    GnnModel,
    Hypothesis,
    Proof,
    Tactic,
    Theorem,
)
from dijla.domain.value_objects import (
    CycleStatus,
    HypothesisSource,
    TheoremStatus,
    Verdict,
    new_id,
)


class TestHypothesis:
    def test_actionable_requires_keyword(self) -> None:
        h = Hypothesis(
            title="GNN robustness",
            statement="Some random words that do not match anything at all in here.",
        )
        assert not h.is_actionable()

    def test_actionable_succeeds_with_keyword(self) -> None:
        h = Hypothesis(
            title="GNN robustness",
            statement="Show that any 3-layer GCN is robust to bounded edge perturbations.",
        )
        assert h.is_actionable()

    def test_immutable(self) -> None:
        h = Hypothesis(
            title="Test",
            statement="A theorem about graph robustness over networks goes here.",
        )
        with pytest.raises(PydanticValidationError):
            h.title = "new"  # type: ignore[misc]

    def test_default_source_is_user(self) -> None:
        h = Hypothesis(title="Test", statement="A theorem about graph robustness today.")
        assert h.source is HypothesisSource.USER


class TestTheorem:
    def test_lean_keyword_required(self) -> None:
        with pytest.raises(PydanticValidationError):
            Theorem(
                hypothesis_id=new_id(),
                name="bad",
                statement_lean="def something := 1",
            )

    def test_with_status_returns_new_instance(self) -> None:
        t = Theorem(
            hypothesis_id=new_id(),
            name="t1",
            statement_lean="theorem t1 : True := by trivial",
        )
        proved = t.with_status(TheoremStatus.PROVED)
        assert proved is not t
        assert proved.status is TheoremStatus.PROVED
        assert t.status is TheoremStatus.OPEN


class TestProof:
    def test_requires_at_least_one_tactic(self) -> None:
        with pytest.raises(PydanticValidationError):
            Proof(theorem_id=new_id(), tactics=(), term="by", elapsed_ms=0)


class TestCertificate:
    def test_round_trip(self) -> None:
        c = Certificate(
            gnn_model_id=new_id(),
            attack_id=new_id(),
            verifier="agnncert",
            verdict=Verdict.PROVED,
            radius=0.1234,
        )
        dumped = c.model_dump()
        rebuilt = Certificate.model_validate(dumped)
        assert rebuilt == c


class TestAttack:
    def test_budget_bounds(self) -> None:
        with pytest.raises(PydanticValidationError):
            Attack(kind=AttackKind.EDGE_PERTURBATION, budget=0)
        with pytest.raises(PydanticValidationError):
            Attack(kind=AttackKind.NODE_INJECTION, budget=10_001)


class TestGnnModel:
    def test_layers_bounded(self) -> None:
        with pytest.raises(PydanticValidationError):
            GnnModel(name="bad", architecture="GCN", layers=0)
        with pytest.raises(PydanticValidationError):
            GnnModel(name="bad", architecture="GCN", layers=65)


class TestCycle:
    def _make(self) -> Cycle:
        return Cycle(hypothesis_id=new_id(), thread_id="t")

    def test_default_status_is_pending(self) -> None:
        assert self._make().status is CycleStatus.PENDING

    def test_with_status_records_completion(self) -> None:
        cycle = self._make().with_status(CycleStatus.COMPLETED, completed=True)
        assert cycle.status is CycleStatus.COMPLETED
        assert cycle.completed_at is not None

    def test_with_interrupt_records_payload(self) -> None:
        cycle = self._make().with_interrupt("approve?", {"k": "v"})
        assert cycle.status is CycleStatus.WAITING_FOR_HUMAN
        assert cycle.interrupt_prompt == "approve?"
        assert cycle.interrupt_payload == {"k": "v"}

    def test_with_result_accumulates_ids(self) -> None:
        cycle = self._make().with_result(theorem_id=new_id(), proof_id=new_id())
        assert cycle.theorem_id is not None
        assert cycle.proof_id is not None
        assert cycle.certificate_id is None


class TestEventAndTactic:
    def test_event_is_immutable(self) -> None:
        e = Event(
            cycle_id=new_id(),
            kind=EventKind.CYCLE_STARTED,
            actor="system",
            payload={"k": 1},
        )
        with pytest.raises(PydanticValidationError):
            e.actor = "x"  # type: ignore[misc]

    def test_tactic_creation(self) -> None:
        t = Tactic(name="exact", body="exact h", description="trivial")
        assert t.name == "exact"


class TestCounterexample:
    def test_payload_preserved(self) -> None:
        c = Counterexample(
            theorem_id=new_id(),
            payload={"graph": [1, 2, 3]},
            note="reason",
        )
        assert c.payload["graph"] == [1, 2, 3]
