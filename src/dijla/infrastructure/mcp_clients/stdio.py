"""Stdio-based MCP clients — connect to the MCP servers as subprocesses.

These are used in production, and optionally in tests when validating the
end-to-end stdio path. Each client implements the same protocol as its
``Direct*`` sibling so callers can swap them transparently.
"""

from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any

from dijla.core.errors import McpToolError


class _StdioClient:
    """Common base — manages an MCP client session over stdio."""

    server_name: str = "unknown"

    def __init__(self, command: str, *args: str) -> None:
        self._command = command
        self._args = list(args)
        self._exit_stack: AsyncExitStack | None = None
        self._session: Any | None = None

    async def __aenter__(self) -> _StdioClient:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        self._exit_stack = AsyncExitStack()
        params = StdioServerParameters(command=self._command, args=self._args)
        read, write = await self._exit_stack.enter_async_context(stdio_client(params))
        session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        self._session = session
        await session.initialize()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
        self._exit_stack = None
        self._session = None

    async def _call(self, tool: str, arguments: dict[str, object]) -> dict[str, object]:
        if self._session is None:
            msg = f"{self.server_name} stdio client is not connected"
            raise RuntimeError(msg)
        try:
            result = await self._session.call_tool(tool, arguments)
        except Exception as exc:
            raise McpToolError(self.server_name, tool, str(exc)) from exc
        if hasattr(result, "model_dump"):
            return dict(result.model_dump())
        if isinstance(result, dict):
            return result
        return {"value": str(result)}


class StdioLean4Client(_StdioClient):
    server_name = "lean4"

    def __init__(self) -> None:
        super().__init__("python", "-m", "dijla.mcp_servers.lean4")

    async def check_tactic(self, theorem_name: str, tactic: str) -> dict[str, object]:
        return await self._call("check_tactic", {"theorem_name": theorem_name, "tactic": tactic})

    async def verify_term(self, theorem_name: str, term: str) -> dict[str, object]:
        return await self._call("verify_term", {"theorem_name": theorem_name, "term": term})


class StdioAgnnCertClient(_StdioClient):
    server_name = "agnncert"

    def __init__(self) -> None:
        super().__init__("python", "-m", "dijla.mcp_servers.agnncert")

    async def certify_graph(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        return await self._call("certify_graph", {"model": model, "attack": attack})


class StdioRcgnnClient(_StdioClient):
    server_name = "rcgnn"

    def __init__(self) -> None:
        super().__init__("python", "-m", "dijla.mcp_servers.rcgnn")

    async def certify_injection(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]:
        return await self._call("certify_injection", {"model": model, "attack": attack})
