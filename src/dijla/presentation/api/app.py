"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dijla.core.logging import configure_logging
from dijla.core.settings import Settings, get_settings
from dijla.presentation.api.deps import build_container
from dijla.presentation.api.exception_handlers import register as register_exception_handlers
from dijla.presentation.api.routes import (
    certificates,
    cycles,
    health,
    hypotheses,
    knowledge_graph,
    theorems,
)


def create_app(settings: Settings | None = None, *, require_human: bool = False) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, json_logs=settings.env != "development")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = build_container(settings, require_human=require_human)
        app.state.container = container
        try:
            yield
        finally:
            pass

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(hypotheses.router)
    app.include_router(cycles.router)
    app.include_router(theorems.router)
    app.include_router(certificates.router)
    app.include_router(knowledge_graph.router)

    return app
