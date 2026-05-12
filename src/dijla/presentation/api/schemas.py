"""Pydantic schemas for API I/O."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import (
    CycleStatus,
    EntityId,
    HypothesisSource,
    TheoremStatus,
    Verdict,
)


class HypothesisCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=10, max_length=4000)
    source: HypothesisSource = HypothesisSource.USER
    submitted_by: str = "anonymous"
    tags: list[str] = []


class HypothesisOut(BaseModel):
    id: EntityId
    title: str
    statement: str
    source: HypothesisSource
    submitted_by: str
    tags: list[str]
    created_at: datetime


class StartCycleIn(BaseModel):
    hypothesis_id: EntityId


class ResumeCycleIn(BaseModel):
    decision: str = Field(min_length=1, max_length=200)


class CycleOut(BaseModel):
    id: EntityId
    hypothesis_id: EntityId
    thread_id: str
    status: CycleStatus
    interrupt_prompt: str | None
    interrupt_payload: dict[str, object] | None
    theorem_id: EntityId | None
    proof_id: EntityId | None
    certificate_id: EntityId | None
    counterexample_id: EntityId | None
    error: str | None
    started_at: datetime
    completed_at: datetime | None


class TheoremOut(BaseModel):
    id: EntityId
    hypothesis_id: EntityId
    name: str
    statement_lean: str
    status: TheoremStatus
    created_at: datetime


class CertificateOut(BaseModel):
    id: EntityId
    gnn_model_id: EntityId
    attack_id: EntityId
    verifier: str
    verdict: Verdict
    radius: float
    proof_artifact_uri: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str = "ok"


class KnowledgeQueryIn(BaseModel):
    cypher: str = Field(min_length=4, max_length=1000)


class KnowledgeQueryOut(BaseModel):
    rows: list[dict[str, object]]
