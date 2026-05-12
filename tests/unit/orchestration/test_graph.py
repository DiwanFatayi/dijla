"""Full LangGraph cycle tests."""

from __future__ import annotations

from typing import Any

import pytest
from langgraph.types import Command

from dijla.domain.entities import Hypothesis
from dijla.domain.value_objects import new_id
from dijla.orchestration.state import ScientificState
from tests.conftest import make_graph


def _initial_state() -> ScientificState:
    return ScientificState(
        cycle_id=new_id(),
        hypothesis=Hypothesis(
            title="bounded perturbation",
            statement="Three-layer GCN is robust to bounded edge perturbations with k=4 graphs.",
        ),
    )


@pytest.mark.asyncio
async def test_graph_runs_full_cycle_without_hitl() -> None:
    graph = make_graph(require_human=False)
    state = _initial_state()
    config: dict[str, Any] = {"configurable": {"thread_id": "t1"}}
    result = await graph.ainvoke(state.model_dump(mode="json"), config=config)
    final = ScientificState.model_validate(result)
    assert final.formal_statement is not None
    assert final.theorem is not None
    assert final.proof is not None
    assert final.certificate is not None
    assert final.critique is not None


@pytest.mark.asyncio
async def test_graph_pauses_on_hitl_then_resumes() -> None:
    graph = make_graph(require_human=True)
    state = _initial_state()
    config: dict[str, Any] = {"configurable": {"thread_id": "t2"}}
    # First invocation triggers an interrupt after formalization.
    await graph.ainvoke(state.model_dump(mode="json"), config=config)
    snapshot = await graph.aget_state(config)
    assert snapshot.tasks
    has_interrupt = any(getattr(task, "interrupts", ()) for task in snapshot.tasks)
    assert has_interrupt

    # Resume with an approval; cycle should run to completion.
    await graph.ainvoke(Command(resume="approve"), config=config)
    # There will be a second interrupt before commit — approve again.
    snapshot = await graph.aget_state(config)
    if any(getattr(task, "interrupts", ()) for task in snapshot.tasks):
        result = await graph.ainvoke(Command(resume="approve"), config=config)
    else:
        result = snapshot.values
    final = ScientificState.model_validate(result)
    assert final.theorem is not None
    assert final.proof is not None
