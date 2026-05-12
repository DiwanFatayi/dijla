"""Direct MCP client smoke tests."""

from __future__ import annotations

from dijla.infrastructure.mcp_clients import (
    DirectAgnnCertClient,
    DirectLean4Client,
    DirectRcgnnClient,
)


async def test_direct_lean4_round_trip() -> None:
    client = DirectLean4Client()
    assert (await client.check_tactic("t", "simp"))["ok"] is True
    assert (await client.apply_tactic("t", "simp"))["ok"] is True
    assert (await client.verify_term("t", "by tauto"))["ok"] is True
    assert "suggestions" in await client.lean_search("simp")


async def test_direct_agnncert_round_trip() -> None:
    client = DirectAgnnCertClient()
    res = await client.certify_graph({"layers": 3}, {"budget": 4})
    assert "radius" in res
    res2 = await client.certify_node({"layers": 3}, {"budget": 4}, node_id=1)
    assert res2["node_id"] == 1
    res3 = await client.sample_attack({"layers": 3}, 0)
    assert res3["budget"] >= 1


async def test_direct_rcgnn_round_trip() -> None:
    client = DirectRcgnnClient()
    res = await client.certify_injection({"layers": 3}, {"budget": 4})
    assert "radius" in res
    res2 = await client.compute_radius({"layers": 3}, {"budget": 4})
    assert set(res2.keys()) == {"radius"}
