"""Smoke-test the FastMCP server builders.

We don't run the stdio loop — we only verify that the servers are constructable
and expose the expected tools.
"""

from __future__ import annotations

from dijla.mcp_servers.agnncert import _build_fastmcp as build_agnncert
from dijla.mcp_servers.lean4 import _build_fastmcp as build_lean4
from dijla.mcp_servers.rcgnn import _build_fastmcp as build_rcgnn


async def test_lean4_server_builds_with_tools() -> None:
    server = build_lean4()
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert {"check_tactic", "apply_tactic", "verify_term", "lean_search"} <= names


async def test_agnncert_server_builds_with_tools() -> None:
    server = build_agnncert()
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert {"certify_graph", "certify_node", "sample_attack"} <= names


async def test_rcgnn_server_builds_with_tools() -> None:
    server = build_rcgnn()
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert {"certify_injection", "compute_radius"} <= names
