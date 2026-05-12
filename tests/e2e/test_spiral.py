"""End-to-end spiral: one cycle and a follow-up cycle that consumes it."""

from __future__ import annotations

from dijla.application.dto import StartCycleCommand, SubmitHypothesisCommand
from dijla.domain.value_objects import HypothesisSource
from dijla.presentation.api.deps import Container


async def test_two_consecutive_cycles_share_knowledge_graph(container: Container) -> None:
    first = await container.submit_hypothesis.execute(
        SubmitHypothesisCommand(
            title="GNN robustness edge perturbation",
            statement="Prove robustness of any 3-layer GCN against bounded edge perturbations.",
        )
    )
    cycle_one = await container.start_cycle.execute(StartCycleCommand(hypothesis_id=first.id))
    assert cycle_one.status.value == "completed"

    # Spiral: enqueue a system-sourced follow-up hypothesis.
    second = await container.submit_hypothesis.execute(
        SubmitHypothesisCommand(
            title="GNN robustness node injection",
            statement="Prove robustness of any 3-layer GCN against node injection attacks.",
            source=HypothesisSource.SPIRAL,
        )
    )
    cycle_two = await container.start_cycle.execute(StartCycleCommand(hypothesis_id=second.id))
    assert cycle_two.status.value == "completed"

    # Knowledge graph grows monotonically across cycles
    theorems = await container.knowledge_graph.query("MATCH (t:Theorem) RETURN t")
    proofs = await container.knowledge_graph.query("MATCH (p:Proof) RETURN p")
    assert len(theorems) == 2
    assert len(proofs) == 2
