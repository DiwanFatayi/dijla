"""Theorem endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from dijla.core.errors import NotFoundError
from dijla.domain.value_objects import EntityId, TheoremStatus
from dijla.presentation.api.schemas import TheoremOut

router = APIRouter(prefix="/api/v1/theorems", tags=["theorems"])


@router.get("", response_model=list[TheoremOut])
async def list_theorems(request: Request, status: TheoremStatus | None = None) -> list[TheoremOut]:
    container = request.app.state.container
    items = await container.list_theorems.execute(status=status)
    return [TheoremOut(**t.model_dump()) for t in items]


@router.get("/{theorem_id}", response_model=TheoremOut)
async def get_theorem(theorem_id: EntityId, request: Request) -> TheoremOut:
    container = request.app.state.container
    try:
        theorem = await container.theorems.get(theorem_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return TheoremOut(**theorem.model_dump())
