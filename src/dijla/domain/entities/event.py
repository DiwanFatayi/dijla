"""Event-sourced cycle history."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class EventKind(StrEnum):
    """Types of events recorded in the cycle ledger."""

    CYCLE_STARTED = "cycle.started"
    AGENT_INVOKED = "agent.invoked"
    AGENT_COMPLETED = "agent.completed"
    TOOL_INVOKED = "tool.invoked"
    TOOL_RESULT = "tool.result"
    HITL_REQUESTED = "hitl.requested"
    HITL_RESUMED = "hitl.resumed"
    KNOWLEDGE_COMMITTED = "knowledge.committed"
    CYCLE_COMPLETED = "cycle.completed"
    CYCLE_FAILED = "cycle.failed"


class Event(BaseModel):
    """An immutable record of an action taken during a cycle."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    cycle_id: EntityId
    kind: EventKind
    actor: str  # "supervisor", "formalizer", ...
    payload: dict[str, object]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
