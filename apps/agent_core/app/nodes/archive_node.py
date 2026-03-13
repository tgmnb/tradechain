from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from apps.agent_core.app.config import get_settings



def _archive_object(state: dict[str, Any], *, state_key: str, object_type: str) -> dict[str, Any]:
    settings = get_settings()
    payload_object = state.get(state_key)
    if not payload_object:
        return {
            **state,
            "messages": [
                *state.get("messages", []),
                {"node": f"archive_{object_type}", "ok": False, "reason": f"no {state_key}"},
            ],
        }

    payload = {
        "object_type": object_type,
        "object_id": payload_object["id"],
        "payload": payload_object,
        "metadata": {
            "chain_type": state.get("chain_type", "intel_update"),
            "request_id": state.get("request_id"),
            "graph": state.get("graph_name", "unknown_graph"),
            "state_key": state_key,
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
        with httpx.Client(timeout=10.0, trust_env=False) as client:
            response = client.post(f"{settings.archive_service_url}/internal/archive", json=payload, headers=headers)
        response.raise_for_status()
        archive_ref = response.json()
        message = {"node": f"archive_{object_type}", "ok": True}
    except Exception as exc:  # noqa: BLE001
        message = {
            "node": f"archive_{object_type}",
            "ok": False,
            "error": str(exc),
            "retryable": True,
            "error_code": "archive_write_failed",
        }

    archive_refs = [*state.get("archive_refs", [])]
    if archive_ref:
        archive_refs.append(archive_ref)

    next_state = {
        **state,
        "archive_refs": archive_refs,
        "current_stage": f"{state_key}_archived",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "messages": [*state.get("messages", []), message],
    }
    if state_key == "proposal":
        next_state["archive_ref"] = archive_ref
    return next_state



def archive_write_node(state: dict[str, Any]) -> dict[str, Any]:
    return _archive_object(state, state_key="proposal", object_type="proposal")



def make_archive_node(*, state_key: str, object_type: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def _node(state: dict[str, Any]) -> dict[str, Any]:
        return _archive_object(state, state_key=state_key, object_type=object_type)

    return _node
