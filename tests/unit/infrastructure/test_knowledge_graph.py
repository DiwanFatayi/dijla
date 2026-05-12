"""In-memory knowledge graph adapter."""

from __future__ import annotations

from dijla.domain.entities import Certificate, Counterexample, Proof, Theorem
from dijla.domain.value_objects import Verdict, new_id
from dijla.infrastructure.graph import InMemoryKnowledgeGraph


async def test_write_and_query_theorem() -> None:
    g = InMemoryKnowledgeGraph()
    t = Theorem(
        hypothesis_id=new_id(),
        name="t1",
        statement_lean="theorem t1 : True := by trivial",
    )
    await g.write_theorem(t)
    rows = await g.query("MATCH (t:Theorem) RETURN t")
    assert len(rows) == 1


async def test_write_proof_certificate_counterexample() -> None:
    g = InMemoryKnowledgeGraph()
    proof = Proof(theorem_id=new_id(), tactics=("simp",), term="by simp", elapsed_ms=1)
    cert = Certificate(
        gnn_model_id=new_id(),
        attack_id=new_id(),
        verifier="agnncert",
        verdict=Verdict.PROVED,
        radius=0.1,
    )
    ce = Counterexample(theorem_id=new_id(), payload={})
    await g.write_proof(proof)
    await g.write_certificate(cert)
    await g.write_counterexample(ce)
    assert len(await g.query("MATCH (p:Proof) RETURN p")) == 1
    assert len(await g.query("MATCH (c:Certificate) RETURN c")) == 1
    assert len(await g.query("MATCH (x:Counterexample) RETURN x")) == 1


async def test_unknown_query_returns_empty() -> None:
    g = InMemoryKnowledgeGraph()
    rows = await g.query("MATCH (n:Nope) RETURN n")
    assert rows == []
