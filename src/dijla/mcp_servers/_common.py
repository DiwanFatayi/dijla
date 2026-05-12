"""Shared helpers for MCP server modules."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash(*parts: object) -> str:
    """Content-addressable hash used by mock verifiers for reproducibility."""
    serialised = json.dumps([_to_jsonable(p) for p in parts], sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialised).hexdigest()[:32]


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    return str(value)
