"""List hypotheses."""

from __future__ import annotations

from dijla.domain.entities import Hypothesis
from dijla.domain.repositories import HypothesisRepository


class ListHypothesesUseCase:
    def __init__(self, hypotheses: HypothesisRepository) -> None:
        self._hypotheses = hypotheses

    async def execute(self) -> list[Hypothesis]:
        return await self._hypotheses.list()
