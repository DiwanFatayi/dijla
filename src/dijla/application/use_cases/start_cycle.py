"""Start a new scientific cycle for a hypothesis."""

from __future__ import annotations

from dijla.application.dto import StartCycleCommand
from dijla.application.services.cycle_service import CycleService
from dijla.domain.entities import Cycle


class StartCycleUseCase:
    def __init__(self, service: CycleService) -> None:
        self._service = service

    async def execute(self, command: StartCycleCommand) -> Cycle:
        return await self._service.start(command.hypothesis_id)
