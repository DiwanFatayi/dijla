"""Shared MCP helpers."""

from __future__ import annotations

from dijla.mcp_servers._common import stable_hash


def test_stable_hash_is_deterministic() -> None:
    a = stable_hash({"x": 1}, "v")
    b = stable_hash({"x": 1}, "v")
    assert a == b


def test_stable_hash_distinguishes_inputs() -> None:
    a = stable_hash({"x": 1})
    b = stable_hash({"x": 2})
    assert a != b


def test_stable_hash_handles_nested_and_non_jsonable() -> None:
    a = stable_hash({"nested": [1, 2, {"k": "v"}], "tuple": (1, 2)}, object())
    assert isinstance(a, str)
    assert len(a) == 32
