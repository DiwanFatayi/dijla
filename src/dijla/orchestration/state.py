"""Typed state for the LangGraph scientific cycle."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.entities import (
    Attack,
    Certificate,
    Counterexample,
    Event,
    GnnModel,
    Hypothesis,
    Proof,
    Theorem,
)
from dijla.domain.value_objects import EntityId


class AgentRoute(StrEnum):
    """Next node selected by the Supervisor."""

    FORMALIZE = "formalize"
    HUMAN_APPROVAL_FORMAL = "human_approval_formal"
    PROVE = "prove"
    VERIFY = "verify"
    CRITIQUE = "critique"
    HUMAN_APPROVAL_COMMIT = "human_approval_commit"
    FINALIZE = "finalize"
    FAILED = "failed"


class ScientificState(BaseModel):
    """State threaded through every node of the LangGraph."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cycle_id: EntityId
    hypothesis: Hypothesis

    # Outputs accumulated by agents
    formal_statement: str | None = None
    theorem: Theorem | None = None
    proof: Proof | None = None
    counterexample: Counterexample | None = None
    gnn_model: GnnModel | None = None
    attacks: list[Attack] = Field(default_factory=list)
    certificate: Certificate | None = None
    critique: str | None = None

    # Orchestration control
    next_step: AgentRoute = AgentRoute.FORMALIZE
    human_decision_formal: str | None = None
    human_decision_commit: str | None = None
    require_human: bool = True

    # Event ledger (within-state; persisted out-of-band as well)
    events: list[Event] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
