from datetime import datetime, timezone
from typing import Any

import httpx

from apps.agent_core.app.config import get_settings


def archive_write_node(state: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    proposal = state.get("proposal")
    if not proposal:
        return {
            **state,
            "messages": [*state.get("messages", []), {"node": "archive_write", "ok": False, "reason": "no proposal"}],
        }

    payload = {
        "object_type": "proposal",
        "object_id": proposal["id"],
        "payload": proposal,
        "metadata": {
            "chain_type": state.get("chain_type", "intel_update"),
            "request_id": state.get("request_id"),
            "graph": "event_to_proposal_graph",
        },
        "storage_type": "minio",
    }
    headers = {
        "X-API-Key": settings.internal_service_api_key,
        "X-Request-ID": state.get("request_id", "unknown"),
        "X-Chain-Type": state.get("chain_type", "intel_update"),
        "X-Actor": state.get("actor", "agent-core"),
    }

    archive_ref: dict[str, Any] | None = None
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(f"{settings.archive_service_url}/internal/archive", json=payload, headers=headers)
        response.raise_for_status()
        archive_ref = response.json()
        message = {"node": "archive_write", "ok": True}
    except Exception as exc:  # noqa: BLE001
        message = {
            "node": "archive_write",
            "ok": False,
            "error": str(exc),
            "retryable": True,
            "error_code": "archive_write_failed",
        }

    return {
        **state,
        "archive_ref": archive_ref,
        "current_stage": "archive_written",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "messages": [*state.get("messages", []), message],
    }
