"""LangGraph StateGraph wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from dijla.orchestration.agents import (
    CriticAgent,
    FormalizerAgent,
    ProverAgent,
    SupervisorAgent,
    VerifierAgent,
)
from dijla.orchestration.state import AgentRoute, ScientificState

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.pregel import Pregel


def build_graph(
    *,
    supervisor: SupervisorAgent,
    formalizer: FormalizerAgent,
    prover: ProverAgent,
    verifier: VerifierAgent,
    critic: CriticAgent,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> Pregel[Any, Any, Any, Any]:
    """Compile the multi-agent supervisor graph.

    Nodes:
      supervisor → formalizer / prover / verifier / critic / HITL / finalize
      Each agent node returns control to the supervisor.
    """

    async def supervisor_node(state: ScientificState) -> dict[str, object]:
        return await supervisor(state)

    async def formalizer_node(state: ScientificState) -> dict[str, object]:
        return await formalizer(state)

    async def prover_node(state: ScientificState) -> dict[str, object]:
        return await prover(state)

    async def verifier_node(state: ScientificState) -> dict[str, object]:
        return await verifier(state)

    async def critic_node(state: ScientificState) -> dict[str, object]:
        return await critic(state)

    async def human_approval_formal_node(state: ScientificState) -> dict[str, object]:
        decision = interrupt(
            {
                "prompt": "Approve the formalized Lean 4 statement?",
                "payload": {
                    "formal_statement": state.formal_statement,
                    "theorem": state.theorem.model_dump(mode="json") if state.theorem else None,
                },
            }
        )
        return {
            "human_decision_formal": str(decision),
            "trace": [*state.trace, f"human approved formalization: {decision}"],
        }

    async def human_approval_commit_node(state: ScientificState) -> dict[str, object]:
        decision = interrupt(
            {
                "prompt": "Commit proof + certificate to the knowledge graph?",
                "payload": {
                    "proof": state.proof.model_dump(mode="json") if state.proof else None,
                    "certificate": state.certificate.model_dump(mode="json")
                    if state.certificate
                    else None,
                },
            }
        )
        return {
            "human_decision_commit": str(decision),
            "trace": [*state.trace, f"human approved commit: {decision}"],
        }

    async def finalize_node(state: ScientificState) -> dict[str, object]:
        return {"trace": [*state.trace, "finalized"]}

    def _route(state: ScientificState) -> str:
        return state.next_step.value

    graph: StateGraph[Any, Any, Any, Any] = StateGraph(ScientificState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node(AgentRoute.FORMALIZE.value, formalizer_node)
    graph.add_node(AgentRoute.HUMAN_APPROVAL_FORMAL.value, human_approval_formal_node)
    graph.add_node(AgentRoute.PROVE.value, prover_node)
    graph.add_node(AgentRoute.VERIFY.value, verifier_node)
    graph.add_node(AgentRoute.CRITIQUE.value, critic_node)
    graph.add_node(AgentRoute.HUMAN_APPROVAL_COMMIT.value, human_approval_commit_node)
    graph.add_node(AgentRoute.FINALIZE.value, finalize_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route,
        {
            AgentRoute.FORMALIZE.value: AgentRoute.FORMALIZE.value,
            AgentRoute.HUMAN_APPROVAL_FORMAL.value: AgentRoute.HUMAN_APPROVAL_FORMAL.value,
            AgentRoute.PROVE.value: AgentRoute.PROVE.value,
            AgentRoute.VERIFY.value: AgentRoute.VERIFY.value,
            AgentRoute.CRITIQUE.value: AgentRoute.CRITIQUE.value,
            AgentRoute.HUMAN_APPROVAL_COMMIT.value: AgentRoute.HUMAN_APPROVAL_COMMIT.value,
            AgentRoute.FINALIZE.value: AgentRoute.FINALIZE.value,
            AgentRoute.FAILED.value: AgentRoute.FINALIZE.value,
        },
    )
    for node in (
        AgentRoute.FORMALIZE,
        AgentRoute.HUMAN_APPROVAL_FORMAL,
        AgentRoute.PROVE,
        AgentRoute.VERIFY,
        AgentRoute.CRITIQUE,
        AgentRoute.HUMAN_APPROVAL_COMMIT,
    ):
        graph.add_edge(node.value, "supervisor")

    graph.add_edge(AgentRoute.FINALIZE.value, END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
