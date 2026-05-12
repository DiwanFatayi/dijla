"""Data transfer objects between presentation and application layers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, HypothesisSource


class SubmitHypothesisCommand(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=10, max_length=4000)
    source: HypothesisSource = HypothesisSource.USER
    submitted_by: str = "anonymous"
    tags: tuple[str, ...] = ()


class StartCycleCommand(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    hypothesis_id: EntityId


class ResumeCycleCommand(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    cycle_id: EntityId
    decision: str  # e.g. "approve" | "reject" | free-form note


class CycleResult(BaseModel):
    """Final shape of a completed cycle."""

    model_config = ConfigDict(frozen=True)

    cycle_id: EntityId
    status: str
    interrupt_prompt: str | None = None
    theorem_id: EntityId | None = None
    proof_id: EntityId | None = None
    certificate_id: EntityId | None = None
    counterexample_id: EntityId | None = None
    error: str | None = None
