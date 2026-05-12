"""Strongly typed identifiers."""

from __future__ import annotations

import uuid
from typing import NewType

EntityId = NewType("EntityId", str)


def new_id() -> EntityId:
    """Mint a new opaque identifier."""
    return EntityId(uuid.uuid4().hex)
