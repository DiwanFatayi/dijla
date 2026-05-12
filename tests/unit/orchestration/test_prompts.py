"""System prompt strings."""

from __future__ import annotations

from dijla.orchestration.prompts import (
    CRITIC_SYSTEM_PROMPT,
    FORMALIZER_SYSTEM_PROMPT,
    PROVER_SYSTEM_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT,
    VERIFIER_SYSTEM_PROMPT,
)


def test_all_prompts_are_non_empty_strings() -> None:
    for prompt in (
        SUPERVISOR_SYSTEM_PROMPT,
        FORMALIZER_SYSTEM_PROMPT,
        PROVER_SYSTEM_PROMPT,
        VERIFIER_SYSTEM_PROMPT,
        CRITIC_SYSTEM_PROMPT,
    ):
        assert isinstance(prompt, str)
        assert len(prompt) > 50
