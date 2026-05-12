"""Submit a hypothesis to the platform."""

from __future__ import annotations

from dijla.application.dto import SubmitHypothesisCommand
from dijla.core.errors import ValidationError
from dijla.domain.entities import Hypothesis
from dijla.domain.repositories import HypothesisRepository


class SubmitHypothesisUseCase:
    """Validate and persist a new hypothesis."""

    def __init__(self, hypotheses: HypothesisRepository) -> None:
        self._hypotheses = hypotheses

    async def execute(self, command: SubmitHypothesisCommand) -> Hypothesis:
        hypothesis = Hypothesis(
            title=command.title,
            statement=command.statement,
            source=command.source,
            submitted_by=command.submitted_by,
            tags=command.tags,
        )
        if not hypothesis.is_actionable():
            msg = (
                "Hypothesis is not actionable: must be ≥32 chars and mention a "
                "platform-relevant keyword (gnn, graph, robust, theorem, lemma, certificate)."
            )
            raise ValidationError(msg)
        await self._hypotheses.add(hypothesis)
        return hypothesis
