"""Map domain errors to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from dijla.core.errors import (
    ConflictError,
    DijlaError,
    HitlPendingError,
    McpToolError,
    NotFoundError,
    ValidationError,
)


def register(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def _conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    async def _validation(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(HitlPendingError)
    async def _hitl(_: Request, exc: HitlPendingError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc), "payload": exc.payload},
        )

    @app.exception_handler(McpToolError)
    async def _mcp(_: Request, exc: McpToolError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": str(exc), "server": exc.server, "tool": exc.tool},
        )

    @app.exception_handler(DijlaError)
    async def _generic(_: Request, exc: DijlaError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
