"""Hypothesis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from dijla.application.dto import SubmitHypothesisCommand
from dijla.core.errors import NotFoundError
from dijla.domain.value_objects import EntityId
from dijla.presentation.api.schemas import HypothesisCreate, HypothesisOut

router = APIRouter(prefix="/api/v1/hypotheses", tags=["hypotheses"])


@router.post("", response_model=HypothesisOut, status_code=201)
async def submit_hypothesis(payload: HypothesisCreate, request: Request) -> HypothesisOut:
    container = request.app.state.container
    command = SubmitHypothesisCommand(
        title=payload.title,
        statement=payload.statement,
        source=payload.source,
        submitted_by=payload.submitted_by,
        tags=tuple(payload.tags),
    )
    hypothesis = await container.submit_hypothesis.execute(command)
    return HypothesisOut(
        **hypothesis.model_dump(),
    )


@router.get("", response_model=list[HypothesisOut])
async def list_hypotheses(request: Request) -> list[HypothesisOut]:
    container = request.app.state.container
    items = await container.list_hypotheses.execute()
    return [HypothesisOut(**i.model_dump()) for i in items]


@router.get("/{hypothesis_id}", response_model=HypothesisOut)
async def get_hypothesis(hypothesis_id: EntityId, request: Request) -> HypothesisOut:
    container = request.app.state.container
    try:
        hypothesis = await container.hypotheses.get(hypothesis_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return HypothesisOut(**hypothesis.model_dump())
