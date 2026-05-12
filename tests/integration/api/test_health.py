"""Health endpoints."""

from __future__ import annotations

from httpx import AsyncClient


async def test_healthz(api_client: AsyncClient) -> None:
    response = await api_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readyz(api_client: AsyncClient) -> None:
    response = await api_client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
