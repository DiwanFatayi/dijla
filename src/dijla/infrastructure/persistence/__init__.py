"""Persistence adapters — in-memory + SQLAlchemy variants."""

from dijla.infrastructure.persistence.in_memory import (
    InMemoryCertificateRepository,
    InMemoryCounterexampleRepository,
    InMemoryCycleRepository,
    InMemoryEventRepository,
    InMemoryHypothesisRepository,
    InMemoryProofRepository,
    InMemoryTacticRepository,
    InMemoryTheoremRepository,
)

__all__ = [
    "InMemoryCertificateRepository",
    "InMemoryCounterexampleRepository",
    "InMemoryCycleRepository",
    "InMemoryEventRepository",
    "InMemoryHypothesisRepository",
    "InMemoryProofRepository",
    "InMemoryTacticRepository",
    "InMemoryTheoremRepository",
]
