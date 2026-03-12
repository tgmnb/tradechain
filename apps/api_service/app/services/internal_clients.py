from uuid import uuid4

import httpx
from fastapi import Request

from apps.api_service.app.core.config import get_settings


class InternalClients:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings

    def headers_from_request(self, request: Request, chain_type: str = "intel_update") -> dict[str, str]:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        actor = request.headers.get("X-Actor", "api-service")
        return {
            "X-Request-ID": request_id,
            "X-Chain-Type": chain_type,
            "X-Actor": actor,
            "X-API-Key": self.settings.internal_service_api_key,
        }

    async def fetch_mock_events(self, request: Request, limit: int = 5) -> list[dict]:
        response = await self._post(
            f"{self.settings.ingestion_service_url}/internal/ingestion/fetch",
            json={"limit": limit},
            headers=self.headers_from_request(request, chain_type="intel_update"),
        )
        return response.get("events", [])

    async def run_event_to_proposal_graph(
        self,
        request: Request,
        event: dict,
        task_id: str | None,
        metadata: dict | None = None,
    ) -> dict:
        return await self._post(
            f"{self.settings.agent_core_service_url}/internal/graphs/event-to-proposal/run",
            json={"event": event, "task_id": task_id, "chain_type": "intel_update", "metadata": metadata or {}},
            headers=self.headers_from_request(request, chain_type="intel_update"),
        )

    async def _post(self, url: str, json: dict, headers: dict[str, str]) -> dict:
        async with httpx.AsyncClient(timeout=self.settings.internal_http_timeout_seconds) as client:
            res = await client.post(url, json=json, headers=headers)
        res.raise_for_status()
        return res.json()


internal_clients = InternalClients()
