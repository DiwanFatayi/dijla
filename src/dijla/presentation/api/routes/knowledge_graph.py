"""Read-only Cypher passthrough."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from dijla.presentation.api.schemas import KnowledgeQueryIn, KnowledgeQueryOut

router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["knowledge-graph"])


@router.post("/query", response_model=KnowledgeQueryOut)
async def query_kg(payload: KnowledgeQueryIn, request: Request) -> KnowledgeQueryOut:
    container = request.app.state.container
    try:
        rows = await container.query_knowledge.execute(payload.cypher)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return KnowledgeQueryOut(rows=rows)
