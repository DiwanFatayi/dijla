"""Graph Neural Network reference."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class GnnModel(BaseModel):
    """A reference to a graph neural network."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    name: str
    architecture: str  # e.g. "GCN", "GAT", "GraphSAGE"
    layers: int = Field(ge=1, le=64)
    weights_uri: str = Field(default="mock://gnn", description="Pointer to weights")
