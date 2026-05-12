"""RCGNN MCP backend tests."""

from __future__ import annotations

from dijla.mcp_servers.rcgnn import RcgnnBackend


async def test_certify_injection_returns_decision() -> None:
    backend = RcgnnBackend()
    result = await backend.certify_injection({"layers": 3}, {"budget": 4})
    assert "radius" in result
    assert result["verdict"] in {"proved", "refuted", "open"}


async def test_certify_injection_refutes_large_budget() -> None:
    backend = RcgnnBackend()
    result = await backend.certify_injection({"layers": 2}, {"budget": 256})
    assert result["verdict"] == "refuted"


async def test_compute_radius_subset() -> None:
    backend = RcgnnBackend()
    result = await backend.compute_radius({"layers": 3}, {"budget": 4})
    assert set(result.keys()) == {"radius"}
