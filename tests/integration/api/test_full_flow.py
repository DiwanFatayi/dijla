"""End-to-end API flow: hypothesis → cycle → theorem → certificate."""

from __future__ import annotations

from httpx import AsyncClient


async def test_submit_hypothesis_and_run_cycle(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "GNN robustness under bounded perturbation",
            "statement": ("Show that any 3-layer GCN is robust to bounded edge perturbations."),
        },
    )
    assert submit.status_code == 201
    hypothesis = submit.json()
    assert hypothesis["title"].startswith("GNN")

    start = await api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis["id"]})
    assert start.status_code == 202
    cycle = start.json()
    assert cycle["status"] == "completed"
    assert cycle["theorem_id"] is not None
    assert cycle["certificate_id"] is not None


async def test_validation_rejects_short_hypothesis(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={"title": "bad", "statement": "Nope, nothing useful here today."},
    )
    # The hypothesis is too generic — domain validation triggers 422.
    assert submit.status_code == 422


async def test_get_cycle_404(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/cycles/does-not-exist")
    assert response.status_code == 404


async def test_get_hypothesis_404(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/hypotheses/does-not-exist")
    assert response.status_code == 404


async def test_list_endpoints_initially_empty(api_client: AsyncClient) -> None:
    for path in (
        "/api/v1/hypotheses",
        "/api/v1/theorems",
        "/api/v1/certificates",
        "/api/v1/cycles",
    ):
        response = await api_client.get(path)
        assert response.status_code == 200
        assert response.json() == []


async def test_theorem_list_after_cycle(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "Robust GCN against injection",
            "statement": ("Prove a robustness theorem for a GCN against node injection attacks."),
        },
    )
    hypothesis_id = submit.json()["id"]
    await api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis_id})

    theorems = await api_client.get("/api/v1/theorems")
    assert theorems.status_code == 200
    items = theorems.json()
    assert len(items) == 1
    assert items[0]["status"] in {"proved", "refuted", "open"}

    proved = await api_client.get("/api/v1/theorems?status=proved")
    assert proved.status_code == 200


async def test_get_theorem_by_id(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "Single theorem fetch",
            "statement": "A theorem about GNN robustness for fetching by id later.",
        },
    )
    hypothesis_id = submit.json()["id"]
    cycle = (await api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis_id})).json()
    theorem = await api_client.get(f"/api/v1/theorems/{cycle['theorem_id']}")
    assert theorem.status_code == 200


async def test_get_theorem_404(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/theorems/does-not-exist")
    assert response.status_code == 404


async def test_knowledge_graph_query(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "knowledge graph theorem about GNN robustness",
            "statement": "Show a robustness theorem to validate the knowledge graph.",
        },
    )
    hypothesis_id = submit.json()["id"]
    await api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis_id})

    query = await api_client.post(
        "/api/v1/knowledge-graph/query",
        json={"cypher": "MATCH (t:Theorem) RETURN t"},
    )
    assert query.status_code == 200
    rows = query.json()["rows"]
    assert len(rows) == 1


async def test_knowledge_graph_rejects_writes(api_client: AsyncClient) -> None:
    response = await api_client.post(
        "/api/v1/knowledge-graph/query",
        json={"cypher": "MATCH (n) DELETE n"},
    )
    assert response.status_code == 400


async def test_resume_cycle_when_not_pending_returns_409(api_client: AsyncClient) -> None:
    submit = await api_client.post(
        "/api/v1/hypotheses",
        json={
            "title": "Resume guard",
            "statement": "GNN robustness theorem for resume guard test case here.",
        },
    )
    hypothesis_id = submit.json()["id"]
    cycle = (await api_client.post("/api/v1/cycles", json={"hypothesis_id": hypothesis_id})).json()
    response = await api_client.post(
        f"/api/v1/cycles/{cycle['id']}/resume",
        json={"decision": "approve"},
    )
    assert response.status_code == 409
