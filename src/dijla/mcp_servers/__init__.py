"""MCP servers.

Each server has:

* a pure-Python ``Backend`` class containing the deterministic logic
  (so it can be reused by the orchestrator in-process and unit-tested);
* a ``FastMCP`` wrapper that exposes the backend's methods as MCP tools over
  stdio for external clients (Claude Desktop, Cursor, etc.).
"""
