---
name: testing-dijla-spiral
description: End-to-end test the Dijla scientific platform — submit hypothesis, start cycle, observe HITL interrupt, resume, verify proved theorem + certificate, and assert the knowledge graph accumulates artefacts across cycles. Use this whenever validating LangGraph orchestrator, MCP server, HITL, or knowledge-graph changes.
---

# Testing the Dijla self-amplifying spiral end-to-end

## What this skill is for
Quickly prove that the platform's core claim — *every proved theorem becomes a blade for the verifier* — still holds end-to-end through the real HTTP API after any change to the orchestrator, agents, MCP servers, or persistence layer.

It also catches the most likely regressions: HITL skipped, resume not forwarding into the graph, KG state not persisting between cycles, certificate verdict/radius going to zero.

## Devin Secrets Needed
None. The PoC ships deterministic in-process mocks; the whole test runs without external API keys, GPUs, or live PostgreSQL / Memgraph / MinIO. (If you want to test against the real adapters, you'd need a Lean 4 + Lake toolchain in the runner image and live PostgreSQL/Memgraph/MinIO, but that's outside this skill's scope.)

## Environment

### Repo layout cheatsheet
- `src/dijla/presentation/api/routes/` — every HTTP endpoint.
- `src/dijla/orchestration/graph.py` — LangGraph wiring; `human_approval_*_node` is where `interrupt()` fires.
- `src/dijla/orchestration/agents/supervisor.py` — router; HITL gates are skipped when their state precondition is already satisfied.
- `src/dijla/infrastructure/graph/client.py` — `InMemoryKnowledgeGraph.query()` only honours `MATCH (Label) RETURN x` for the labels `Theorem`, `Proof`, `Certificate`, `Counterexample`. Don't try fancier Cypher against the in-memory KG.
- `tests/e2e/test_spiral.py` — the same flow as a programmatic test.

### Default app vs test app
`dijla.main:app` calls `create_app()` with `require_human=False`, so HITL doesn't fire. **To test HITL, launch with `require_human=True`** using a small launcher:

```bash
cat > /tmp/_e2e_app.py <<'PY'
from dijla.presentation.api import create_app
app = create_app(require_human=True)
PY

cd /path/to/dijla
source .venv/bin/activate
PYTHONPATH=/tmp:src uvicorn _e2e_app:app --host 127.0.0.1 --port 8000 &
```

Docker-compose is overkill for this skill — the in-memory stack exercises every code path used in CI.

## Standard commands

```bash
# install deps
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

# lint / format / type-check / tests
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest             # 115 tests, ≥85% coverage gate
```

## The 9-step API walk

Replace `<HYP_ID>` / `<CYCLE_ID>` with values pulled from earlier responses.

```bash
# 1. health
curl -s http://127.0.0.1:8000/healthz
# expect {"status":"ok"}

# 2. submit hypothesis A
curl -s -X POST http://127.0.0.1:8000/api/v1/hypotheses \
  -H 'content-type: application/json' \
  -d '{"title":"GCN robustness","statement":"Every 2-layer GCN on bounded-degree graphs is robust to budget-1 edge perturbations.","source":"user"}'
# 201 with UUID id

# 3. start cycle A — expect HITL pause
curl -s -X POST http://127.0.0.1:8000/api/v1/cycles \
  -H 'content-type: application/json' \
  -d '{"hypothesis_id":"<HYP_ID>"}'
# 202, status=waiting_for_human,
# interrupt_prompt="Commit proof + certificate to the knowledge graph?",
# interrupt_payload contains the proof + certificate,
# all artefact IDs null

# 4. paused state persists
curl -s http://127.0.0.1:8000/api/v1/cycles/<CYCLE_ID>

# 5. resume with "approve"
curl -s -X POST http://127.0.0.1:8000/api/v1/cycles/<CYCLE_ID>/resume \
  -H 'content-type: application/json' \
  -d '{"decision":"approve"}'
# 200, status=completed, theorem_id / proof_id / certificate_id all non-null

# 6. proved theorem and certificate are committed
curl -s 'http://127.0.0.1:8000/api/v1/theorems?status=proved'
curl -s http://127.0.0.1:8000/api/v1/certificates
# expect verdict=proved, radius>0

# 7. KG contains the theorem
curl -s -X POST http://127.0.0.1:8000/api/v1/knowledge-graph/query \
  -H 'content-type: application/json' \
  -d '{"cypher":"MATCH (t:Theorem) RETURN t"}'
# expect rows length 1

# 8. repeat for hypothesis B (different statement)
# 9. final KG query — expect rows length 2 for BOTH Theorem and Certificate
```

## Things that have surprised previous testers

- **HITL fires at the commit gate, not the formal-approval gate** — even with `require_human=True`. The supervisor's formal-approval branch is currently dead code because the formalizer sets `state.theorem` before the supervisor re-evaluates. This might change in the future; check `agents/supervisor.py` if you see a different interrupt prompt.
- **`interrupt_prompt` / `interrupt_payload` are not cleared on COMPLETED.** Don't assume they're null after the cycle finishes; check `status` instead.
- **The in-memory KG ignores most of the Cypher string** — it only switches on the label substring. Don't write WHERE clauses and expect them to filter.
- **All mocks are deterministic.** Re-running the same hypothesis produces the same UUIDs/proofs/certificates within a process but new UUIDs across processes (the UUIDs are generated on each call). The shape and verdict are stable.
- **`radius=0.367879` for `rcgnn` is the expected fixture** (it's `e^(-1/(layers+1))` with the default GNN layers=3, budget=1). If you see `radius=0`, the verifier is returning `refuted` or the bound calculation broke.

## Production adapters (out of scope for this skill, but worth knowing)

Everything is swappable via DI in `src/dijla/presentation/api/deps.py`. To switch to real backends:

| Adapter | Toggle |
| --- | --- |
| LangGraph checkpointer | `LANGGRAPH_CHECKPOINT_BACKEND=postgres` + DSN |
| Knowledge graph | replace `InMemoryKnowledgeGraph` with `MemgraphClient(host, port)` |
| Artefact store | replace `InMemoryArtifactStore` with `MinioArtifactStore(...)` |
| MCP clients | replace `DirectXxxClient` with `StdioXxxClient` (subprocess `python -m dijla.mcp_servers.xxx`) |
| Repositories | replace `InMemoryXxxRepository` with the SQLAlchemy `XxxRepository` in `infrastructure/persistence/` |

None of these require code changes outside the deps wiring.