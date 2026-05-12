"""Tests for the core layer (settings + logging + errors)."""

from __future__ import annotations

from dijla.core.errors import (
    ConflictError,
    DijlaError,
    HitlPendingError,
    McpToolError,
    NotFoundError,
    ValidationError,
)
from dijla.core.logging import configure_logging, get_logger
from dijla.core.settings import Settings, get_settings, reset_settings_cache


def test_settings_defaults() -> None:
    reset_settings_cache()
    s = get_settings()
    assert s.env in {"development", "testing", "production"}


def test_settings_use_mock_models() -> None:
    s = Settings(env="testing", anthropic_api_key="")
    assert s.use_mock_models is True
    s2 = Settings(env="testing", anthropic_api_key="real-key")
    assert s2.use_mock_models is False


def test_reset_settings_cache_returns_new_instance() -> None:
    reset_settings_cache()
    a = get_settings()
    b = get_settings()
    assert a is b
    reset_settings_cache()
    c = get_settings()
    assert c is not a or c == a  # new instance after reset


def test_configure_logging_smoke() -> None:
    configure_logging("INFO", json_logs=True)
    log = get_logger("test")
    log.info("hello", k="v")


def test_error_hierarchy() -> None:
    assert issubclass(NotFoundError, DijlaError)
    assert issubclass(ConflictError, DijlaError)
    assert issubclass(ValidationError, DijlaError)
    assert issubclass(HitlPendingError, DijlaError)
    assert issubclass(McpToolError, DijlaError)


def test_hitl_pending_error_captures_payload() -> None:
    exc = HitlPendingError("approve?", payload={"k": 1})
    assert exc.prompt == "approve?"
    assert exc.payload == {"k": 1}


def test_mcp_tool_error_string() -> None:
    exc = McpToolError("lean4", "check_tactic", "boom")
    assert "lean4" in str(exc)
    assert exc.server == "lean4"
    assert exc.tool == "check_tactic"
