"""Integration test for the HITL interrupt/resume flow."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from dijla.core.settings import Settings
from dijla.presentation.api import create_app


@pytest_asyncio.fixture
async def hitl_api_client():
    settings = Settings(env="testing", log_level="WARNING")
    app = create_app(settings, require_human=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with app.router.lifespan_context(app):
            yield client


@pytest.mark.asyncio
async def test_hitl_pauses_then_resumes(hitl_api_client: AsyncClient) -> None:
    submit = await hitl_api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "HITL test",
            "statement": "A graph robustness theorem that needs human approval today.",
        },
    )
    hypothesis_id = submit.json()["id"]
    cycle = (
        await hitl_api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis_id})
    ).json()
    # First pause: after formalization
    assert cycle["status"] == "waiting_for_human"
    assert cycle["interrupt_prompt"] is not None

    cycle = (
        await hitl_api_client.post(
            f"/api/v1/cycles/{cycle['id']}/resume",
            json={"decision": "approve"},
        )
    ).json()
    # After resume, the cycle may pause again at the commit gate
    assert cycle["status"] in {"waiting_for_human", "completed"}

    if cycle["status"] == "waiting_for_human":
        cycle = (
            await hitl_api_client.post(
                f"/api/v1/cycles/{cycle['id']}/resume",
                json={"decision": "approve"},
            )
        ).json()
    assert cycle["status"] == "completed"
