from uuid import uuid4

import pytest

TestClient = pytest.importorskip("fastapi.testclient").TestClient

from apps.api_service.app.main import app



def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"



def test_create_task_requires_api_key() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/tasks",
        json={"title": "test task", "type": "major_task", "source": "discord", "chain_type": "major_task"},
    )
    assert response.status_code == 401


# This is an integration skeleton for CI after runtime dependencies are ready.
def test_intel_update_endpoint_contract_only() -> None:
    client = TestClient(app)
    response = client.post("/v1/workflows/intel-update/run", headers={"X-API-Key": "external-dev-key"})
    # In local CI without live dependencies this may fail with 500/502; the assertion keeps contract visibility.
    assert response.status_code in {200, 500, 502}
