"""Build the appropriate LangGraph checkpointer for the environment."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import MemorySaver


def build_checkpointer(
    backend: str = "memory",
    *,
    dsn: str | None = None,
) -> Any:
    """Return a LangGraph checkpointer for the requested backend.

    The PostgreSQL and SQLite back-ends are returned as async context manager
    factories; callers must enter them. The in-memory back-end is returned
    directly because it requires no setup.
    """
    if backend == "memory":
        return MemorySaver()
    if backend == "sqlite":
        if dsn is None:
            msg = "sqlite checkpointer requires `dsn`"
            raise ValueError(msg)
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        return AsyncSqliteSaver.from_conn_string(dsn)
    if backend == "postgres":
        if dsn is None:
            msg = "postgres checkpointer requires `dsn`"
            raise ValueError(msg)
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        return AsyncPostgresSaver.from_conn_string(dsn)
    msg = f"Unknown checkpointer backend: {backend}"
    raise ValueError(msg)
