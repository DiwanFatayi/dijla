"""Lean 4 MCP backend tests."""

from __future__ import annotations

from dijla.mcp_servers.lean4 import Lean4Backend


async def test_closing_tactic_returns_term() -> None:
    backend = Lean4Backend()
    result = await backend.check_tactic("t1", "exact GNN.robustness.proof N a")
    assert result["ok"] is True
    assert result["closes_goal"] is True
    assert "term" in result


async def test_progress_tactic_does_not_close() -> None:
    backend = Lean4Backend()
    result = await backend.check_tactic("t1", "intro G N a")
    assert result["ok"] is True
    assert result.get("closes_goal") is False


async def test_unknown_tactic_fails() -> None:
    backend = Lean4Backend()
    result = await backend.check_tactic("t1", "magic_unknown_tactic")
    assert result["ok"] is False
    assert "error" in result


async def test_verify_term_accepts_by_prefix() -> None:
    backend = Lean4Backend()
    result = await backend.verify_term("t1", "by tauto")
    assert result["ok"] is True


async def test_verify_term_rejects_invalid() -> None:
    backend = Lean4Backend()
    result = await backend.verify_term("t1", "not a proof")
    assert result["ok"] is False


async def test_lean_search_returns_suggestions() -> None:
    backend = Lean4Backend()
    result = await backend.lean_search("simp")
    assert any("simp" in s for s in result["suggestions"])


async def test_apply_tactic_is_alias_for_check_tactic() -> None:
    backend = Lean4Backend()
    a = await backend.apply_tactic("t1", "intro G N a")
    b = await backend.check_tactic("t1", "intro G N a")
    assert a["ok"] == b["ok"]
