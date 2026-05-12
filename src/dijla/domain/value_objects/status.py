"""Enums for domain status fields."""

from __future__ import annotations

from enum import StrEnum


class HypothesisSource(StrEnum):
    """Where a hypothesis came from."""

    USER = "user"
    SYSTEM = "system"
    SPIRAL = "spiral"


class TheoremStatus(StrEnum):
    """Lifecycle of a theorem."""

    OPEN = "open"
    PROVED = "proved"
    REFUTED = "refuted"


class CycleStatus(StrEnum):
    """Lifecycle of a scientific cycle."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in {CycleStatus.COMPLETED, CycleStatus.FAILED, CycleStatus.CANCELLED}


class Verdict(StrEnum):
    """Binary scientific outcome of a verification."""

    PROVED = "proved"
    REFUTED = "refuted"
    OPEN = "open"
