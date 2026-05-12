"""Tactic — reusable proof step shipped to the Lean MCP server."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import EntityId, new_id


class Tactic(BaseModel):
    """A named Lean 4 tactic."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    name: str
    body: str
    description: str = ""
