"""SQLAlchemy 2 ORM models. Used by the optional PostgreSQL adapters."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base."""


class HypothesisRow(Base):
    __tablename__ = "hypotheses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    statement: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(32))
    submitted_by: Mapped[str] = mapped_column(String(120), default="anonymous")
    tags: Mapped[list[Any]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TheoremRow(Base):
    __tablename__ = "theorems"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    hypothesis_id: Mapped[str] = mapped_column(String(64), ForeignKey("hypotheses.id"))
    name: Mapped[str] = mapped_column(String(120))
    statement_lean: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CycleRow(Base):
    __tablename__ = "cycles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    hypothesis_id: Mapped[str] = mapped_column(String(64), ForeignKey("hypotheses.id"))
    thread_id: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32))
    interrupt_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    interrupt_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    theorem_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    proof_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    certificate_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    counterexample_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EventRow(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    cycle_id: Mapped[str] = mapped_column(String(64), ForeignKey("cycles.id"))
    kind: Mapped[str] = mapped_column(String(48))
    actor: Mapped[str] = mapped_column(String(48))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProofRow(Base):
    __tablename__ = "proofs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    theorem_id: Mapped[str] = mapped_column(String(64), ForeignKey("theorems.id"))
    tactics: Mapped[list[Any]] = mapped_column(JSON)
    term: Mapped[str] = mapped_column(Text)
    elapsed_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CertificateRow(Base):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    gnn_model_id: Mapped[str] = mapped_column(String(64))
    attack_id: Mapped[str] = mapped_column(String(64))
    verifier: Mapped[str] = mapped_column(String(32))
    verdict: Mapped[str] = mapped_column(String(16))
    radius: Mapped[float] = mapped_column()
    proof_artifact_uri: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
