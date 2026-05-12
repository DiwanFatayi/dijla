"""List all cycles."""

from __future__ import annotations

from dijla.domain.entities import Cycle
from dijla.domain.repositories import CycleRepository


class ListCyclesUseCase:
    def __init__(self, cycles: CycleRepository) -> None:
        self._cycles = cycles

    async def execute(self) -> list[Cycle]:
        return await self._cycles.list()
