import httpx
import pytest

from apps.api_service.app.api.workflows import run_intel_update
from apps.api_service.app.main import app
from apps.api_service.app.services.internal_clients import internal_clients


@pytest.mark.anyio
async def test_healthz() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_create_task_requires_api_key() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/tasks",
            json={"title": "test task", "type": "major_task", "source": "discord", "chain_type": "major_task"},
        )
    assert response.status_code == 401


# This is an integration skeleton for CI after runtime dependencies are ready.
@pytest.mark.anyio
async def test_intel_update_endpoint_contract_only() -> None:
    class DummySession:
        def commit(self) -> None:
            return None

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key"}

    original_fetch = internal_clients.fetch_mock_events

    async def fake_fetch_mock_events(request, limit: int = 5) -> list[dict]:
        return []

    internal_clients.fetch_mock_events = fake_fetch_mock_events
    try:
        response = await run_intel_update(DummyRequest(), DummySession())
    finally:
        internal_clients.fetch_mock_events = original_fetch
    assert response == {
        "status": "success",
        "ingested": 0,
        "created_events": 0,
        "created_proposals": 0,
    }
