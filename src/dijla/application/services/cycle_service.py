"""Application service that drives a LangGraph scientific cycle.

This service is the seam between the orchestrator (LangGraph) and the rest of
the application. It is responsible for:

* persisting the ``Cycle`` row + event ledger
* invoking the compiled graph with the right thread id
* detecting LangGraph ``interrupt`` events and surfacing them as
  ``CycleStatus.WAITING_FOR_HUMAN``
* committing the final theorem / proof / certificate / counterexample to
  PostgreSQL + Memgraph + MinIO when a cycle completes
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from langgraph.types import Command

from dijla.core.errors import HitlPendingError
from dijla.core.logging import get_logger
from dijla.domain.entities import (
    Certificate,
    Counterexample,
    Cycle,
    Event,
    EventKind,
    Proof,
    Theorem,
)
from dijla.domain.repositories import (
    CertificateRepository,
    CounterexampleRepository,
    CycleRepository,
    EventRepository,
    HypothesisRepository,
    ProofRepository,
    TheoremRepository,
)
from dijla.domain.value_objects import (
    CycleStatus,
    EntityId,
    TheoremStatus,
    Verdict,
    new_id,
)
from dijla.orchestration.state import ScientificState

log = get_logger("dijla.cycle_service")


class KnowledgeGraphWriter(Protocol):
    async def write_theorem(self, theorem: Theorem) -> None: ...
    async def write_proof(self, proof: Proof) -> None: ...
    async def write_certificate(self, certificate: Certificate) -> None: ...
    async def write_counterexample(self, counterexample: Counterexample) -> None: ...


class ArtifactWriter(Protocol):
    async def put(self, bucket: str, key: str, data: bytes) -> str: ...
    async def ensure_buckets(self, buckets: list[str]) -> None: ...


class CycleService:
    """Coordinates LangGraph execution with persistence and HITL."""

    def __init__(
        self,
        *,
        graph: Any,
        hypotheses: HypothesisRepository,
        cycles: CycleRepository,
        events: EventRepository,
        theorems: TheoremRepository,
        proofs: ProofRepository,
        certificates: CertificateRepository,
        counterexamples: CounterexampleRepository,
        knowledge_graph: KnowledgeGraphWriter,
        artifacts: ArtifactWriter,
        artifact_buckets: tuple[str, str, str, str] = (
            "proofs",
            "certificates",
            "attacks",
            "models",
        ),
    ) -> None:
        self._graph = graph
        self._hypotheses = hypotheses
        self._cycles = cycles
        self._events = events
        self._theorems = theorems
        self._proofs = proofs
        self._certificates = certificates
        self._counterexamples = counterexamples
        self._kg = knowledge_graph
        self._artifacts = artifacts
        self._artifact_buckets = list(artifact_buckets)

    async def start(self, hypothesis_id: EntityId) -> Cycle:
        hypothesis = await self._hypotheses.get(hypothesis_id)
        thread_id = f"cycle-{new_id()}"
        cycle = Cycle(
            hypothesis_id=hypothesis.id,
            thread_id=thread_id,
            status=CycleStatus.RUNNING,
        )
        await self._cycles.add(cycle)
        await self._append_event(
            cycle.id, EventKind.CYCLE_STARTED, "system", {"thread_id": thread_id}
        )

        initial = ScientificState(cycle_id=cycle.id, hypothesis=hypothesis)
        cycle = await self._run_until_complete_or_interrupt(cycle, initial.model_dump(mode="json"))
        return cycle

    async def resume(self, cycle_id: EntityId, decision: str) -> Cycle:
        cycle = await self._cycles.get(cycle_id)
        if cycle.status is not CycleStatus.WAITING_FOR_HUMAN:
            msg = f"Cycle {cycle_id} is not waiting for human input (status={cycle.status})"
            raise HitlPendingError(prompt=msg, payload={"current_status": cycle.status.value})

        await self._append_event(cycle.id, EventKind.HITL_RESUMED, "human", {"decision": decision})
        cycle = cycle.with_status(CycleStatus.RUNNING)
        await self._cycles.update(cycle)
        cycle = await self._run_until_complete_or_interrupt(cycle, Command(resume=decision))
        return cycle

    async def _run_until_complete_or_interrupt(
        self,
        cycle: Cycle,
        payload: Any,
    ) -> Cycle:
        config = {"configurable": {"thread_id": cycle.thread_id}}
        try:
            result = await self._graph.ainvoke(payload, config=config)
        except Exception as exc:
            log.exception("cycle_failed", cycle_id=cycle.id)
            cycle = cycle.with_status(CycleStatus.FAILED, error=str(exc), completed=True)
            await self._cycles.update(cycle)
            await self._append_event(
                cycle.id, EventKind.CYCLE_FAILED, "system", {"error": str(exc)}
            )
            return cycle

        graph_state = await self._graph.aget_state(config)
        interrupts = self._extract_interrupts(graph_state)
        if interrupts:
            prompt = str(interrupts[0].get("prompt", "Human input required"))
            raw_payload = interrupts[0].get("payload", {})
            interrupt_payload: dict[str, object] = (
                dict(raw_payload) if isinstance(raw_payload, dict) else {"value": raw_payload}
            )
            cycle = cycle.with_interrupt(prompt=prompt, payload=interrupt_payload)
            await self._cycles.update(cycle)
            await self._append_event(
                cycle.id,
                EventKind.HITL_REQUESTED,
                "supervisor",
                {"prompt": prompt, "payload": interrupt_payload},
            )
            return cycle

        # Cycle completed successfully — commit artefacts.
        state = ScientificState.model_validate(result)
        cycle = await self._commit(cycle, state)
        return cycle

    @staticmethod
    def _extract_interrupts(graph_state: Any) -> list[dict[str, object]]:
        tasks = getattr(graph_state, "tasks", ()) or ()
        out: list[dict[str, object]] = []
        for task in tasks:
            for interrupt in getattr(task, "interrupts", ()) or ():
                value = getattr(interrupt, "value", interrupt)
                if isinstance(value, dict):
                    out.append(value)
                else:
                    out.append({"prompt": "Human input required", "payload": value})
        return out

    async def _commit(self, cycle: Cycle, state: ScientificState) -> Cycle:
        update: dict[str, EntityId | None] = {}

        if state.theorem is not None:
            theorem = state.theorem
            if state.proof is not None:
                theorem = theorem.with_status(TheoremStatus.PROVED)
            elif state.counterexample is not None:
                theorem = theorem.with_status(TheoremStatus.REFUTED)
            try:
                await self._theorems.add(theorem)
            except Exception:
                await self._theorems.update(theorem)
            await self._kg.write_theorem(theorem)
            update["theorem_id"] = theorem.id

        if state.proof is not None:
            await self._proofs.add(state.proof)
            await self._kg.write_proof(state.proof)
            await self._artifacts.ensure_buckets(self._artifact_buckets)
            await self._artifacts.put(
                "proofs",
                f"{state.proof.id}.lean",
                state.proof.term.encode("utf-8"),
            )
            update["proof_id"] = state.proof.id

        if state.certificate is not None:
            await self._certificates.add(state.certificate)
            await self._kg.write_certificate(state.certificate)
            await self._artifacts.put(
                "certificates",
                f"{state.certificate.id}.json",
                state.certificate.model_dump_json().encode("utf-8"),
            )
            update["certificate_id"] = state.certificate.id

        if state.counterexample is not None:
            await self._counterexamples.add(state.counterexample)
            await self._kg.write_counterexample(state.counterexample)
            update["counterexample_id"] = state.counterexample.id

        await self._append_event(
            cycle.id,
            EventKind.KNOWLEDGE_COMMITTED,
            "supervisor",
            {
                "theorem_id": update.get("theorem_id"),
                "verdict": state.certificate.verdict.value
                if state.certificate is not None
                else Verdict.OPEN.value,
            },
        )
        cycle = cycle.with_result(**update).with_status(CycleStatus.COMPLETED, completed=True)
        cycle = cycle.model_copy(update={"completed_at": datetime.now(UTC)})
        await self._cycles.update(cycle)
        await self._append_event(
            cycle.id, EventKind.CYCLE_COMPLETED, "system", {"status": cycle.status.value}
        )
        return cycle

    async def _append_event(
        self,
        cycle_id: EntityId,
        kind: EventKind,
        actor: str,
        payload: dict[str, object],
    ) -> None:
        event = Event(cycle_id=cycle_id, kind=kind, actor=actor, payload=payload)
        await self._events.append(event)
