"""Counterexample entity."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class Counterexample(BaseModel):
    """A concrete (graph, model) pair refuting a theorem."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    theorem_id: EntityId
    payload: dict[str, object]
    note: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
