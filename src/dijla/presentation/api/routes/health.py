"""Liveness + readiness."""

from __future__ import annotations

from fastapi import APIRouter

from dijla.presentation.api.schemas import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/readyz", response_model=HealthResponse, tags=["health"])
async def readyz() -> HealthResponse:
    return HealthResponse(status="ready")
