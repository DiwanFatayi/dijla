"""Domain-level errors. Infrastructure converts them to HTTP responses."""

from __future__ import annotations


class DijlaError(Exception):
    """Base class for all platform errors."""


class NotFoundError(DijlaError):
    """An entity was not found."""


class ConflictError(DijlaError):
    """A write conflicts with the current state of the world."""


class ValidationError(DijlaError):
    """The caller provided an invalid value."""


class HitlPendingError(DijlaError):
    """The cycle is paused waiting on a scientist."""

    def __init__(self, prompt: str, payload: object) -> None:
        super().__init__(prompt)
        self.prompt = prompt
        self.payload = payload


class McpToolError(DijlaError):
    """An MCP tool execution failed."""

    def __init__(self, server: str, tool: str, reason: str) -> None:
        super().__init__(f"MCP {server}.{tool} failed: {reason}")
        self.server = server
        self.tool = tool
        self.reason = reason
