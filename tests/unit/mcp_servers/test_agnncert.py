"""AGNNCert MCP backend tests."""

from __future__ import annotations

from dijla.mcp_servers.agnncert import AgnnCertBackend


async def test_certify_graph_returns_radius() -> None:
    backend = AgnnCertBackend()
    result = await backend.certify_graph({"layers": 3}, {"kind": "edge_perturbation", "budget": 4})
    assert result["radius"] > 0
    assert result["verdict"] in {"proved", "refuted", "open"}


async def test_certify_graph_refutes_large_budget() -> None:
    backend = AgnnCertBackend()
    result = await backend.certify_graph({"layers": 2}, {"budget": 256})
    assert result["verdict"] == "refuted"
    assert result["radius"] == 0


async def test_sample_attack_is_deterministic() -> None:
    backend = AgnnCertBackend()
    a = await backend.sample_attack({"layers": 3}, 7)
    b = await backend.sample_attack({"layers": 3}, 7)
    assert a == b


async def test_certify_node_includes_node_id() -> None:
    backend = AgnnCertBackend()
    result = await backend.certify_node({"layers": 3}, {"budget": 2}, node_id=42)
    assert result["node_id"] == 42
