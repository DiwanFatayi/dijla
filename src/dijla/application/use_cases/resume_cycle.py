"""Resume a cycle that is waiting on a human decision (HITL)."""

from __future__ import annotations

from dijla.application.dto import ResumeCycleCommand
from dijla.application.services.cycle_service import CycleService
from dijla.domain.entities import Cycle


class ResumeCycleUseCase:
    def __init__(self, service: CycleService) -> None:
        self._service = service

    async def execute(self, command: ResumeCycleCommand) -> Cycle:
        return await self._service.resume(command.cycle_id, command.decision)
