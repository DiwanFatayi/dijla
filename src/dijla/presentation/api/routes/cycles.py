"""Cycle endpoints — including HITL resume."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from dijla.application.dto import ResumeCycleCommand, StartCycleCommand
from dijla.core.errors import NotFoundError
from dijla.domain.entities import Cycle
from dijla.domain.value_objects import EntityId
from dijla.presentation.api.schemas import CycleOut, ResumeCycleIn, StartCycleIn

router = APIRouter(prefix="/api/v1/cycles", tags=["cycles"])


def _to_out(cycle: Cycle) -> CycleOut:
    return CycleOut(**cycle.model_dump())


@router.post("", response_model=CycleOut, status_code=202)
async def start_cycle(payload: StartCycleIn, request: Request) -> CycleOut:
    container = request.app.state.container
    try:
        cycle = await container.start_cycle.execute(
            StartCycleCommand(hypothesis_id=payload.hypothesis_id)
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_out(cycle)


@router.get("", response_model=list[CycleOut])
async def list_cycles(request: Request) -> list[CycleOut]:
    container = request.app.state.container
    items = await container.list_cycles.execute()
    return [_to_out(c) for c in items]


@router.get("/{cycle_id}", response_model=CycleOut)
async def get_cycle(cycle_id: EntityId, request: Request) -> CycleOut:
    container = request.app.state.container
    try:
        cycle = await container.cycles.get(cycle_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_out(cycle)


@router.post("/{cycle_id}/resume", response_model=CycleOut)
async def resume_cycle(cycle_id: EntityId, payload: ResumeCycleIn, request: Request) -> CycleOut:
    container = request.app.state.container
    try:
        cycle = await container.resume_cycle.execute(
            ResumeCycleCommand(cycle_id=cycle_id, decision=payload.decision)
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_out(cycle)
