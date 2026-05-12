"""Theorem entity — the formalised question, with a status."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from dijla.domain.value_objects import EntityId, TheoremStatus, new_id


class Theorem(BaseModel):
    """A theorem expressed in Lean 4 syntax."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    hypothesis_id: EntityId
    name: str = Field(min_length=1, max_length=120)
    statement_lean: str = Field(min_length=8)
    status: TheoremStatus = TheoremStatus.OPEN
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("statement_lean")
    @classmethod
    def must_look_like_lean(cls, value: str) -> str:
        if "theorem" not in value and "lemma" not in value:
            msg = "Lean 4 statement must contain a `theorem` or `lemma` keyword."
            raise ValueError(msg)
        return value

    def with_status(self, status: TheoremStatus) -> Theorem:
        """Return a new theorem with the new status (entities are immutable)."""
        return self.model_copy(update={"status": status})
