"""Tests for value objects."""

from __future__ import annotations

import pytest

from dijla.domain.value_objects import (
    CycleStatus,
    HypothesisSource,
    TheoremStatus,
    Verdict,
    new_id,
)


def test_new_id_is_unique() -> None:
    ids = {new_id() for _ in range(100)}
    assert len(ids) == 100
    for i in ids:
        assert len(i) == 32  # uuid4 hex


def test_cycle_status_terminal() -> None:
    for status in (CycleStatus.COMPLETED, CycleStatus.FAILED, CycleStatus.CANCELLED):
        assert status.is_terminal
    for status in (
        CycleStatus.PENDING,
        CycleStatus.RUNNING,
        CycleStatus.WAITING_FOR_HUMAN,
    ):
        assert not status.is_terminal


@pytest.mark.parametrize(
    "enum_cls,value",
    [
        (HypothesisSource, "user"),
        (HypothesisSource, "system"),
        (HypothesisSource, "spiral"),
        (TheoremStatus, "open"),
        (TheoremStatus, "proved"),
        (TheoremStatus, "refuted"),
        (Verdict, "proved"),
        (Verdict, "refuted"),
        (Verdict, "open"),
    ],
)
def test_string_enum_round_trip(enum_cls: type, value: str) -> None:
    assert enum_cls(value).value == value
