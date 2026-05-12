"""Tests for the in-memory repository implementations."""

from __future__ import annotations

import pytest

from dijla.core.errors import NotFoundError
from dijla.domain.entities import (
    Certificate,
    Counterexample,
    Cycle,
    Event,
    EventKind,
    Hypothesis,
    Proof,
    Tactic,
    Theorem,
)
from dijla.domain.value_objects import TheoremStatus, Verdict, new_id
from dijla.infrastructure.persistence import (
    InMemoryCertificateRepository,
    InMemoryCounterexampleRepository,
    InMemoryCycleRepository,
    InMemoryEventRepository,
    InMemoryHypothesisRepository,
    InMemoryProofRepository,
    InMemoryTacticRepository,
    InMemoryTheoremRepository,
)


async def test_hypothesis_round_trip() -> None:
    repo = InMemoryHypothesisRepository()
    h = Hypothesis(title="test title", statement="GNN robustness theorem about graphs goes here.")
    await repo.add(h)
    assert (await repo.get(h.id)).id == h.id
    listed = await repo.list()
    assert listed == [h]


async def test_hypothesis_missing_raises() -> None:
    repo = InMemoryHypothesisRepository()
    with pytest.raises(NotFoundError):
        await repo.get(new_id())


async def test_theorem_update_and_list_filter() -> None:
    repo = InMemoryTheoremRepository()
    t = Theorem(
        hypothesis_id=new_id(),
        name="t1",
        statement_lean="theorem t1 : True := by trivial",
    )
    await repo.add(t)
    proved = t.with_status(TheoremStatus.PROVED)
    await repo.update(proved)
    assert (await repo.get(t.id)).status is TheoremStatus.PROVED
    proved_list = await repo.list(status=TheoremStatus.PROVED)
    open_list = await repo.list(status=TheoremStatus.OPEN)
    assert len(proved_list) == 1
    assert len(open_list) == 0


async def test_theorem_update_missing_raises() -> None:
    repo = InMemoryTheoremRepository()
    t = Theorem(
        hypothesis_id=new_id(),
        name="t1",
        statement_lean="theorem t1 : True := by trivial",
    )
    with pytest.raises(NotFoundError):
        await repo.update(t)


async def test_proof_round_trip() -> None:
    repo = InMemoryProofRepository()
    p = Proof(theorem_id=new_id(), tactics=("simp",), term="by simp", elapsed_ms=10)
    await repo.add(p)
    assert (await repo.get(p.id)).id == p.id
    with pytest.raises(NotFoundError):
        await repo.get(new_id())


async def test_certificate_round_trip() -> None:
    repo = InMemoryCertificateRepository()
    c = Certificate(
        gnn_model_id=new_id(),
        attack_id=new_id(),
        verifier="agnncert",
        verdict=Verdict.PROVED,
        radius=0.1,
    )
    await repo.add(c)
    assert await repo.list() == [c]


async def test_counterexample_round_trip() -> None:
    repo = InMemoryCounterexampleRepository()
    ce = Counterexample(theorem_id=new_id(), payload={"k": 1})
    await repo.add(ce)
    items = await repo.list()
    assert items == [ce]


async def test_cycle_round_trip() -> None:
    repo = InMemoryCycleRepository()
    c = Cycle(hypothesis_id=new_id(), thread_id="t")
    await repo.add(c)
    assert (await repo.get(c.id)).id == c.id
    with pytest.raises(NotFoundError):
        await repo.get(new_id())
    with pytest.raises(NotFoundError):
        await repo.update(Cycle(hypothesis_id=new_id(), thread_id="x"))


async def test_event_append_and_list() -> None:
    repo = InMemoryEventRepository()
    cycle_id = new_id()
    e = Event(cycle_id=cycle_id, kind=EventKind.CYCLE_STARTED, actor="system", payload={})
    await repo.append(e)
    items = await repo.list_for_cycle(cycle_id)
    assert items == [e]


async def test_event_stream() -> None:
    repo = InMemoryEventRepository()
    cycle_id = new_id()
    e = Event(cycle_id=cycle_id, kind=EventKind.CYCLE_STARTED, actor="system", payload={})
    await repo.append(e)
    gen = await repo.stream(cycle_id)
    collected = [item async for item in gen]
    assert collected == [e]


async def test_tactic_round_trip() -> None:
    repo = InMemoryTacticRepository()
    t = Tactic(name="simp", body="simp")
    await repo.add(t)
    items = await repo.list()
    assert items == [t]
