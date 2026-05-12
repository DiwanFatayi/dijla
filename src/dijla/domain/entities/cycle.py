"""Cycle — one full pass through the scientific spiral."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from dijla.domain.value_objects import CycleStatus, EntityId, new_id


class Cycle(BaseModel):
    """A run of the LangGraph orchestrator for a single hypothesis."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: EntityId = Field(default_factory=new_id)
    hypothesis_id: EntityId
    thread_id: str  # LangGraph checkpoint thread id
    status: CycleStatus = CycleStatus.PENDING
    interrupt_prompt: str | None = None
    interrupt_payload: dict[str, object] | None = None
    theorem_id: EntityId | None = None
    proof_id: EntityId | None = None
    certificate_id: EntityId | None = None
    counterexample_id: EntityId | None = None
    error: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def with_status(
        self,
        status: CycleStatus,
        *,
        error: str | None = None,
        completed: bool = False,
    ) -> Cycle:
        update: dict[str, object] = {"status": status}
        if error is not None:
            update["error"] = error
        if completed:
            update["completed_at"] = datetime.now(UTC)
        return self.model_copy(update=update)

    def with_interrupt(self, prompt: str, payload: dict[str, object]) -> Cycle:
        return self.model_copy(
            update={
                "status": CycleStatus.WAITING_FOR_HUMAN,
                "interrupt_prompt": prompt,
                "interrupt_payload": payload,
            }
        )

    def with_result(
        self,
        *,
        theorem_id: EntityId | None = None,
        proof_id: EntityId | None = None,
        certificate_id: EntityId | None = None,
        counterexample_id: EntityId | None = None,
    ) -> Cycle:
        update: dict[str, object] = {}
        if theorem_id is not None:
            update["theorem_id"] = theorem_id
        if proof_id is not None:
            update["proof_id"] = proof_id
        if certificate_id is not None:
            update["certificate_id"] = certificate_id
        if counterexample_id is not None:
            update["counterexample_id"] = counterexample_id
        return self.model_copy(update=update)
