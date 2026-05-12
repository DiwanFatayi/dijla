"""Proof entity."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class Proof(BaseModel):
    """A Lean 4 proof of a Theorem."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    theorem_id: EntityId
    tactics: tuple[str, ...] = Field(min_length=1)
    term: str = Field(min_length=1)
    elapsed_ms: int = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
