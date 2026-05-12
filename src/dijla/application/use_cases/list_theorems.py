"""List theorems with optional status filter."""

from __future__ import annotations

from dijla.domain.entities import Theorem
from dijla.domain.repositories import TheoremRepository
from dijla.domain.value_objects import TheoremStatus


class ListTheoremsUseCase:
    def __init__(self, theorems: TheoremRepository) -> None:
        self._theorems = theorems

    async def execute(self, *, status: TheoremStatus | None = None) -> list[Theorem]:
        return await self._theorems.list(status=status)
