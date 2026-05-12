"""Base protocol for an agent node."""

from __future__ import annotations

from typing import Protocol

from dijla.orchestration.state import ScientificState


class AgentProtocol(Protocol):
    """An agent is an async callable that updates the state."""

    name: str

    async def __call__(self, state: ScientificState) -> dict[str, object]: ...


AgentNode = AgentProtocol
