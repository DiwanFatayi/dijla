"""Hypothesis entity — the entry point to the scientific cycle."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, HypothesisSource, new_id


class Hypothesis(BaseModel):
    """A scientific question to be investigated."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=10, max_length=4000)
    source: HypothesisSource = HypothesisSource.USER
    submitted_by: str = "anonymous"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tags: tuple[str, ...] = ()

    def is_actionable(self) -> bool:
        """Hypotheses below a hard floor of detail are rejected upstream."""
        return len(self.statement) >= 32 and any(
            keyword in self.statement.lower()
            for keyword in ("gnn", "graph", "robust", "theorem", "lemma", "certificate")
        )
