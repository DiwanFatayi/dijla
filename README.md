# Dijla

> Dual-core self-amplifying scientific platform for **formal mathematics ⊕
> graph neural network certification**.

`dijla` runs the full scientific-method cycle for the intersection of formal
mathematics and GNN robustness. Two cores power each other:

* **Prover core** — Nazrin Prover + Goedel-Prover-V2 32B: proves theorems
  about GNN robustness in Lean 4 / mathlib4.
* **Verifier core** — AGNNCert + RCGNN: deterministically certifies GNN
  robustness against adversarial and node-injection attacks.

Every proved theorem becomes a *blade* for the verifier, and every
counterexample becomes a new *challenge* for the prover. The two cores meet
in a Memgraph knowledge graph that grows with every spiral iteration.

## Architecture (one paragraph)

A LangGraph **Supervisor** orchestrates four specialised agents
(*Formalizer*, *Prover*, *Verifier*, *Critic*) that talk to Lean 4, AGNNCert
and RCGNN through **MCP** tool servers. State and HITL interrupts are
persisted via a LangGraph PostgreSQL checkpointer; long-term tactics and
counterexamples live in a LangGraph `BaseStore`. Knowledge facts are written
to Memgraph and binary artefacts to MinIO.

For the full design see [`PLAN.md`](./PLAN.md) and
[`ARCHITECTURE.md`](./ARCHITECTURE.md).

## Quick start

```bash
# 1. Install dev deps
uv sync --all-extras --dev          # or: uv pip install -e ".[dev]"

# 2. Run the test suite (in-memory mocks — no docker required)
pytest

# 3. Lint + type-check
ruff check . && ruff format --check . && mypy src

# 4. Run the full local stack
docker compose up --build
```

The FastAPI app listens on `http://localhost:8000`. OpenAPI docs are served at
`/docs`.

### Smoke a single spiral cycle

```bash
dijla smoke
```

This submits a sample hypothesis, runs the LangGraph orchestrator end-to-end
(with mocks), and prints the resulting cycle id.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/hypotheses` | Submit a hypothesis |
| `GET`  | `/api/v1/hypotheses` | List hypotheses |
| `POST` | `/api/v1/cycles` | Start a scientific cycle |
| `GET`  | `/api/v1/cycles/{id}` | Inspect a cycle |
| `POST` | `/api/v1/cycles/{id}/resume` | HITL — resume a paused cycle |
| `GET`  | `/api/v1/theorems` | List theorems (filter by status) |
| `GET`  | `/api/v1/certificates` | List certificates |
| `POST` | `/api/v1/knowledge-graph/query` | Read-only Cypher passthrough |
| `GET`  | `/healthz`, `/readyz` | Health probes |

## Sandbox limitations

Real SOTA model weights (Goedel-Prover-V2 32B, Aria, Claude Opus 4.7) require
GPUs and paid APIs that are unavailable in the sandbox. The orchestrator runs
with deterministic mock adapters that exercise the *full* cycle. Production
deploys swap in real model backends via the same protocols — no orchestrator
changes are required. See [`ARCHITECTURE.md` §8](./ARCHITECTURE.md) for
details.

## License

MIT.
