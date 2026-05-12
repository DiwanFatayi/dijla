"""Uvicorn entrypoint: ``uvicorn dijla.main:app``."""

from __future__ import annotations

from dijla.presentation.api import create_app

app = create_app()
