"""Verifier agent — calls AGNNCert / RCGNN MCP tools for certification."""

from __future__ import annotations

from typing import Protocol

from dijla.domain.entities import (
    Attack,
    AttackKind,
    Certificate,
    GnnModel,
)
from dijla.domain.value_objects import Verdict
from dijla.orchestration.state import ScientificState


class AgnnCertToolProtocol(Protocol):
    async def certify_graph(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]: ...


class RcgnnToolProtocol(Protocol):
    async def certify_injection(
        self, model: dict[str, object], attack: dict[str, object]
    ) -> dict[str, object]: ...


class VerifierAgent:
    """Picks the right verifier MCP server for each attack."""

    name = "verifier"

    def __init__(self, agnncert: AgnnCertToolProtocol, rcgnn: RcgnnToolProtocol) -> None:
        self._agnncert = agnncert
        self._rcgnn = rcgnn

    async def __call__(self, state: ScientificState) -> dict[str, object]:
        gnn = state.gnn_model or GnnModel(name="default_gcn", architecture="GCN", layers=3)
        attacks = list(state.attacks) or [
            Attack(kind=AttackKind.EDGE_PERTURBATION, budget=8),
            Attack(kind=AttackKind.NODE_INJECTION, budget=4),
        ]

        certificates: list[Certificate] = []
        for attack in attacks:
            if attack.kind is AttackKind.NODE_INJECTION:
                result = await self._rcgnn.certify_injection(
                    {"id": gnn.id, "architecture": gnn.architecture, "layers": gnn.layers},
                    {"id": attack.id, "kind": attack.kind, "budget": attack.budget},
                )
                verifier_name = "rcgnn"
            else:
                result = await self._agnncert.certify_graph(
                    {"id": gnn.id, "architecture": gnn.architecture, "layers": gnn.layers},
                    {"id": attack.id, "kind": attack.kind, "budget": attack.budget},
                )
                verifier_name = "agnncert"
            verdict = Verdict(str(result.get("verdict", Verdict.OPEN.value)))
            radius_value = result.get("radius", 0.0)
            radius = float(radius_value) if isinstance(radius_value, (int, float, str)) else 0.0
            certificates.append(
                Certificate(
                    gnn_model_id=gnn.id,
                    attack_id=attack.id,
                    verifier=verifier_name,
                    verdict=verdict,
                    radius=radius,
                    proof_artifact_uri=str(result.get("artifact_uri", "mock://artifact")),
                )
            )

        # The cycle's headline certificate is the minimum-radius PROVED one,
        # otherwise the first REFUTED one, otherwise the first OPEN one.
        headline = next(
            (
                c
                for c in sorted(certificates, key=lambda c: c.radius)
                if c.verdict is Verdict.PROVED
            ),
            None,
        )
        if headline is None:
            headline = next((c for c in certificates if c.verdict is Verdict.REFUTED), None)
        if headline is None:
            headline = certificates[0]

        trace = [
            *state.trace,
            f"verifier produced {len(certificates)} certificates; headline verdict={headline.verdict.value}",
        ]
        return {
            "gnn_model": gnn,
            "attacks": attacks,
            "certificate": headline,
            "trace": trace,
        }
