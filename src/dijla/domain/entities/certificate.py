"""Certificate — deterministic verifier output."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, Verdict, new_id


class Certificate(BaseModel):
    """Output of AGNNCert / RCGNN for a (model, attack) pair."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, protected_namespaces=())

    id: EntityId = Field(default_factory=new_id)
    gnn_model_id: EntityId
    attack_id: EntityId
    verifier: str = Field(min_length=1)  # "agnncert" | "rcgnn"
    verdict: Verdict
    radius: float = Field(ge=0.0)
    proof_artifact_uri: str = "mock://artifact"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
