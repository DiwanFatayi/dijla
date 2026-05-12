"""Application-layer use-case tests."""

from __future__ import annotations

import pytest

from dijla.application.dto import (
    ResumeCycleCommand,
    StartCycleCommand,
    SubmitHypothesisCommand,
)
from dijla.application.use_cases import (
    ListHypothesesUseCase,
    QueryKnowledgeGraphUseCase,
)
from dijla.core.errors import HitlPendingError, NotFoundError, ValidationError
from dijla.domain.value_objects import CycleStatus, HypothesisSource, new_id
from dijla.infrastructure.persistence import InMemoryHypothesisRepository
from dijla.presentation.api.deps import Container


class TestSubmitHypothesis:
    async def test_persists_hypothesis(self, container: Container) -> None:
        hypothesis = await container.submit_hypothesis.execute(
            SubmitHypothesisCommand(
                title="GNN robustness",
                statement="Show that any 3-layer GCN is robust under perturbation bounded by k.",
            )
        )
        assert (await container.hypotheses.get(hypothesis.id)).id == hypothesis.id

    async def test_rejects_non_actionable(self, container: Container) -> None:
        with pytest.raises(ValidationError):
            await container.submit_hypothesis.execute(
                SubmitHypothesisCommand(
                    title="Too short",
                    statement="Nope, nothing useful here at all today.",
                )
            )

    async def test_source_is_recorded(self, container: Container) -> None:
        hypothesis = await container.submit_hypothesis.execute(
            SubmitHypothesisCommand(
                title="System-generated",
                statement="Auto-generated graph robustness theorem suggestion from spiral.",
                source=HypothesisSource.SYSTEM,
            )
        )
        assert hypothesis.source is HypothesisSource.SYSTEM


class TestListHypotheses:
    async def test_empty(self) -> None:
        repo = InMemoryHypothesisRepository()
        result = await ListHypothesesUseCase(repo).execute()
        assert result == []


class TestStartCycle:
    async def test_full_cycle_runs_to_completion(
        self, container: Container, submitted_hypothesis
    ) -> None:
        cycle = await container.start_cycle.execute(
            StartCycleCommand(hypothesis_id=submitted_hypothesis.id)
        )
        assert cycle.status is CycleStatus.COMPLETED
        assert cycle.theorem_id is not None
        assert cycle.proof_id is not None
        assert cycle.certificate_id is not None
        # Theorem should have been promoted to PROVED in the repository
        theorem = await container.theorems.get(cycle.theorem_id)
        assert theorem.status.value == "proved"

    async def test_missing_hypothesis_raises(self, container: Container) -> None:
        with pytest.raises(NotFoundError):
            await container.start_cycle.execute(StartCycleCommand(hypothesis_id=new_id()))


class TestResumeCycle:
    async def test_resume_requires_paused_cycle(
        self, container: Container, submitted_hypothesis
    ) -> None:
        cycle = await container.start_cycle.execute(
            StartCycleCommand(hypothesis_id=submitted_hypothesis.id)
        )
        assert cycle.status is CycleStatus.COMPLETED
        with pytest.raises(HitlPendingError):
            await container.resume_cycle.execute(
                ResumeCycleCommand(cycle_id=cycle.id, decision="approve")
            )


class TestQueryKnowledgeGraph:
    async def test_rejects_writes(self, container: Container) -> None:
        with pytest.raises(ValueError, match="Read-only"):
            await container.query_knowledge.execute("MATCH (n) DELETE n")

    async def test_returns_empty_for_unknown_label(self, container: Container) -> None:
        use_case = QueryKnowledgeGraphUseCase(container.knowledge_graph)
        rows = await use_case.execute("MATCH (n:Nothing) RETURN n")
        assert rows == []
