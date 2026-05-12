"""Shared pytest fixtures."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from dijla.application.dto import SubmitHypothesisCommand
from dijla.core.settings import Settings
from dijla.domain.entities import Hypothesis
from dijla.orchestration.agents import (
    CriticAgent,
    FormalizerAgent,
    ProverAgent,
    SupervisorAgent,
    VerifierAgent,
)
from dijla.orchestration.graph import build_graph
from dijla.presentation.api.deps import Container, build_container

os.environ.setdefault("LANGGRAPH_ALLOWED_MSGPACK_MODULES", "*")


@pytest.fixture
def settings() -> Settings:
    return Settings(env="testing", log_level="WARNING")


@pytest.fixture
def container(settings: Settings) -> Container:
    return build_container(settings, require_human=False)


@pytest.fixture
def hitl_container(settings: Settings) -> Container:
    return build_container(settings, require_human=True)


@pytest.fixture
def sample_hypothesis_command() -> SubmitHypothesisCommand:
    return SubmitHypothesisCommand(
        title="GNN robustness under bounded edge perturbation",
        statement=(
            "Show that any 3-layer GCN is robust to bounded edge perturbations "
            "with a non-trivial certified radius."
        ),
    )


@pytest_asyncio.fixture
async def submitted_hypothesis(
    container: Container, sample_hypothesis_command: SubmitHypothesisCommand
) -> Hypothesis:
    return await container.submit_hypothesis.execute(sample_hypothesis_command)


@pytest_asyncio.fixture
async def api_client(settings: Settings) -> AsyncIterator[AsyncClient]:
    from dijla.presentation.api import create_app

    app = create_app(settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with app.router.lifespan_context(app):
            yield client


def make_graph(*, require_human: bool = False) -> Any:
    """Build a fresh compiled graph for unit tests of the orchestrator."""
    from dijla.infrastructure.mcp_clients import (
        DirectAgnnCertClient,
        DirectLean4Client,
        DirectRcgnnClient,
    )

    return build_graph(
        supervisor=SupervisorAgent(require_human=require_human),
        formalizer=FormalizerAgent(),
        prover=ProverAgent(DirectLean4Client()),
        verifier=VerifierAgent(DirectAgnnCertClient(), DirectRcgnnClient()),
        critic=CriticAgent(),
    )
