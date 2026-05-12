"""Dependency wiring for FastAPI."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from dijla.application.services.cycle_service import CycleService
from dijla.application.use_cases import (
    ListCyclesUseCase,
    ListHypothesesUseCase,
    ListTheoremsUseCase,
    QueryKnowledgeGraphUseCase,
    ResumeCycleUseCase,
    StartCycleUseCase,
    SubmitHypothesisUseCase,
)
from dijla.core.settings import Settings, get_settings
from dijla.infrastructure.graph import InMemoryKnowledgeGraph
from dijla.infrastructure.mcp_clients import (
    DirectAgnnCertClient,
    DirectLean4Client,
    DirectRcgnnClient,
)
from dijla.infrastructure.object_store import InMemoryArtifactStore
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
from dijla.orchestration.agents import (
    CriticAgent,
    FormalizerAgent,
    ProverAgent,
    SupervisorAgent,
    VerifierAgent,
)
from dijla.orchestration.graph import build_graph


@dataclass
class Container:
    """Singletons resolved at app startup."""

    settings: Settings
    hypotheses: InMemoryHypothesisRepository
    theorems: InMemoryTheoremRepository
    proofs: InMemoryProofRepository
    certificates: InMemoryCertificateRepository
    counterexamples: InMemoryCounterexampleRepository
    cycles: InMemoryCycleRepository
    events: InMemoryEventRepository
    tactics: InMemoryTacticRepository
    knowledge_graph: InMemoryKnowledgeGraph
    artifacts: InMemoryArtifactStore
    cycle_service: CycleService
    submit_hypothesis: SubmitHypothesisUseCase
    list_hypotheses: ListHypothesesUseCase
    list_theorems: ListTheoremsUseCase
    list_cycles: ListCyclesUseCase
    start_cycle: StartCycleUseCase
    resume_cycle: ResumeCycleUseCase
    query_knowledge: QueryKnowledgeGraphUseCase
    graph: Any


def build_container(settings: Settings | None = None, *, require_human: bool = False) -> Container:
    """Build the dependency container.

    The default PoC container uses in-memory repositories and direct (in-process)
    MCP clients. Production containers swap these out via dedicated factories.
    """
    settings = settings or get_settings()

    hypotheses = InMemoryHypothesisRepository()
    theorems = InMemoryTheoremRepository()
    proofs = InMemoryProofRepository()
    certificates = InMemoryCertificateRepository()
    counterexamples = InMemoryCounterexampleRepository()
    cycles = InMemoryCycleRepository()
    events = InMemoryEventRepository()
    tactics = InMemoryTacticRepository()
    knowledge_graph = InMemoryKnowledgeGraph()
    artifacts = InMemoryArtifactStore()

    supervisor = SupervisorAgent(require_human=require_human)
    formalizer = FormalizerAgent()
    prover = ProverAgent(DirectLean4Client())
    verifier = VerifierAgent(DirectAgnnCertClient(), DirectRcgnnClient())
    critic = CriticAgent()

    graph = build_graph(
        supervisor=supervisor,
        formalizer=formalizer,
        prover=prover,
        verifier=verifier,
        critic=critic,
    )

    cycle_service = CycleService(
        graph=graph,
        hypotheses=hypotheses,
        cycles=cycles,
        events=events,
        theorems=theorems,
        proofs=proofs,
        certificates=certificates,
        counterexamples=counterexamples,
        knowledge_graph=knowledge_graph,
        artifacts=artifacts,
    )

    return Container(
        settings=settings,
        hypotheses=hypotheses,
        theorems=theorems,
        proofs=proofs,
        certificates=certificates,
        counterexamples=counterexamples,
        cycles=cycles,
        events=events,
        tactics=tactics,
        knowledge_graph=knowledge_graph,
        artifacts=artifacts,
        cycle_service=cycle_service,
        submit_hypothesis=SubmitHypothesisUseCase(hypotheses),
        list_hypotheses=ListHypothesesUseCase(hypotheses),
        list_theorems=ListTheoremsUseCase(theorems),
        list_cycles=ListCyclesUseCase(cycles),
        start_cycle=StartCycleUseCase(cycle_service),
        resume_cycle=ResumeCycleUseCase(cycle_service),
        query_knowledge=QueryKnowledgeGraphUseCase(knowledge_graph),
        graph=graph,
    )


async def lifespan(settings: Settings) -> AsyncIterator[Container]:
    """FastAPI lifespan that yields a fully wired container."""
    container = build_container(settings)
    yield container
