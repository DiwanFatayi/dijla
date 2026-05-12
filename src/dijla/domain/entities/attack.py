"""Attack specification (adversarial perturbation, node injection, etc.)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class AttackKind(StrEnum):
    """Family of attack."""

    EDGE_PERTURBATION = "edge_perturbation"
    FEATURE_PERTURBATION = "feature_perturbation"
    NODE_INJECTION = "node_injection"


class Attack(BaseModel):
    """An adversarial attack specification."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    kind: AttackKind
    budget: int = Field(ge=1, le=10_000)
    description: str = ""
