"""Typer CLI — quick smoke commands for the platform."""

from __future__ import annotations

import asyncio

import typer

from dijla.application.dto import StartCycleCommand, SubmitHypothesisCommand
from dijla.presentation.api.deps import build_container

app = typer.Typer(help="Dijla scientific platform CLI.", no_args_is_help=True)


@app.callback()
def _root_callback() -> None:
    """Dijla command entry."""


@app.command(name="smoke")
def smoke_cmd() -> None:
    """Submit one hypothesis and run a single cycle (mocks)."""

    async def _run() -> None:
        container = build_container()
        hypothesis = await container.submit_hypothesis.execute(
            SubmitHypothesisCommand(
                title="GNN robustness under bounded edge perturbation",
                statement=(
                    "Show that any 3-layer GCN is robust to bounded edge "
                    "perturbations with a non-trivial radius."
                ),
            )
        )
        cycle = await container.start_cycle.execute(StartCycleCommand(hypothesis_id=hypothesis.id))
        typer.echo(f"hypothesis: {hypothesis.id}")
        typer.echo(f"cycle: {cycle.id} status={cycle.status.value}")

    asyncio.run(_run())


if __name__ == "__main__":  # pragma: no cover
    app()
