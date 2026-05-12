"""In-memory repositories — used by tests and the default PoC config.

These are deliberately simple. Production deploys swap in the SQLAlchemy
implementations in ``sqlalchemy_repos.py``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from dijla.core.errors import NotFoundError
from dijla.domain.entities import (
    Certificate,
    Counterexample,
    Cycle,
    Event,
    Hypothesis,
    Proof,
    Tactic,
    Theorem,
)
from dijla.domain.value_objects import EntityId, TheoremStatus


class InMemoryHypothesisRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Hypothesis] = {}

    async def add(self, hypothesis: Hypothesis) -> None:
        self._store[hypothesis.id] = hypothesis

    async def get(self, hypothesis_id: EntityId) -> Hypothesis:
        try:
            return self._store[hypothesis_id]
        except KeyError as e:
            raise NotFoundError(f"Hypothesis {hypothesis_id} not found") from e

    async def list(self) -> list[Hypothesis]:
        return sorted(self._store.values(), key=lambda h: h.created_at)


class InMemoryTheoremRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Theorem] = {}

    async def add(self, theorem: Theorem) -> None:
        self._store[theorem.id] = theorem

    async def update(self, theorem: Theorem) -> None:
        if theorem.id not in self._store:
            raise NotFoundError(f"Theorem {theorem.id} not found")
        self._store[theorem.id] = theorem

    async def get(self, theorem_id: EntityId) -> Theorem:
        try:
            return self._store[theorem_id]
        except KeyError as e:
            raise NotFoundError(f"Theorem {theorem_id} not found") from e

    async def list(self, *, status: TheoremStatus | None = None) -> list[Theorem]:
        results = sorted(self._store.values(), key=lambda t: t.created_at)
        if status is not None:
            results = [t for t in results if t.status is status]
        return results


class InMemoryProofRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Proof] = {}

    async def add(self, proof: Proof) -> None:
        self._store[proof.id] = proof

    async def get(self, proof_id: EntityId) -> Proof:
        try:
            return self._store[proof_id]
        except KeyError as e:
            raise NotFoundError(f"Proof {proof_id} not found") from e


class InMemoryCertificateRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Certificate] = {}

    async def add(self, certificate: Certificate) -> None:
        self._store[certificate.id] = certificate

    async def list(self) -> list[Certificate]:
        return sorted(self._store.values(), key=lambda c: c.created_at)


class InMemoryCounterexampleRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Counterexample] = {}

    async def add(self, counterexample: Counterexample) -> None:
        self._store[counterexample.id] = counterexample

    async def list(self) -> list[Counterexample]:
        return sorted(self._store.values(), key=lambda c: c.created_at)


class InMemoryCycleRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Cycle] = {}

    async def add(self, cycle: Cycle) -> None:
        self._store[cycle.id] = cycle

    async def update(self, cycle: Cycle) -> None:
        if cycle.id not in self._store:
            raise NotFoundError(f"Cycle {cycle.id} not found")
        self._store[cycle.id] = cycle

    async def get(self, cycle_id: EntityId) -> Cycle:
        try:
            return self._store[cycle_id]
        except KeyError as e:
            raise NotFoundError(f"Cycle {cycle_id} not found") from e

    async def list(self) -> list[Cycle]:
        return sorted(self._store.values(), key=lambda c: c.started_at)


class InMemoryEventRepository:
    def __init__(self) -> None:
        self._store: list[Event] = []

    async def append(self, event: Event) -> None:
        self._store.append(event)

    async def stream(self, cycle_id: EntityId) -> AsyncIterator[Event]:
        async def _gen() -> AsyncIterator[Event]:
            for event in self._store:
                if event.cycle_id == cycle_id:
                    yield event

        return _gen()

    async def list_for_cycle(self, cycle_id: EntityId) -> list[Event]:
        return [e for e in self._store if e.cycle_id == cycle_id]


class InMemoryTacticRepository:
    def __init__(self) -> None:
        self._store: dict[EntityId, Tactic] = {}

    async def add(self, tactic: Tactic) -> None:
        self._store[tactic.id] = tactic

    async def list(self) -> list[Tactic]:
        return list(self._store.values())
