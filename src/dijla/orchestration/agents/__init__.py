"""Agents — one per role. Each is an async callable on the ScientificState."""

from dijla.orchestration.agents.base import AgentNode, AgentProtocol
from dijla.orchestration.agents.critic import CriticAgent
from dijla.orchestration.agents.formalizer import FormalizerAgent
from dijla.orchestration.agents.prover import ProverAgent
from dijla.orchestration.agents.supervisor import SupervisorAgent
from dijla.orchestration.agents.verifier import VerifierAgent

__all__ = [
    "AgentNode",
    "AgentProtocol",
    "CriticAgent",
    "FormalizerAgent",
    "ProverAgent",
    "SupervisorAgent",
    "VerifierAgent",
]
