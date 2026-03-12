from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status

from apps.agent_core.app.graphs.event_to_proposal import build_event_to_proposal_graph
from libs.contracts.graph import GraphRunRequest, GraphRunResponse

router = APIRouter(prefix="/internal/graphs", tags=["graphs"])
graph = build_event_to_proposal_graph()


def require_internal_key(x_api_key: str | None = Header(default=None)) -> None:
    from os import getenv

    expected = getenv("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal API key")


@router.post("/event-to-proposal/run", response_model=GraphRunResponse, dependencies=[Depends(require_internal_key)])
async def run_event_to_proposal(
    payload: GraphRunRequest,
    x_request_id: str | None = Header(default=None),
    x_chain_type: str | None = Header(default="intel_update"),
    x_actor: str | None = Header(default="api-service"),
) -> GraphRunResponse:
    state = {
        "task_id": str(payload.task_id) if payload.task_id else None,
        "chain_type": payload.chain_type or x_chain_type or "intel_update",
        "event": payload.event or {},
        "metadata": payload.metadata,
        "request_id": x_request_id or str(uuid4()),
        "actor": x_actor,
        "messages": [],
    }
    result = graph.invoke(state)
    proposal = result.get("proposal")
    if not proposal:
        return GraphRunResponse(
            graph_name="event_to_proposal_graph",
            status="failed",
            requires_human=False,
            proposal=None,
            archive_ref=result.get("archive_ref"),
            messages=result.get("messages", []),
            finished_at=datetime.now(timezone.utc),
        )

    return GraphRunResponse(
        graph_name="event_to_proposal_graph",
        status="needs_human" if proposal.get("requires_human") else "completed",
        requires_human=proposal.get("requires_human", False),
        proposal=proposal,
        archive_ref=result.get("archive_ref"),
        messages=result.get("messages", []),
        finished_at=datetime.now(timezone.utc),
    )


@router.post("/review/run", dependencies=[Depends(require_internal_key)])
async def run_review_placeholder(payload: GraphRunRequest) -> dict:
    return _placeholder("review_graph", payload)


@router.post("/evaluation/run", dependencies=[Depends(require_internal_key)])
async def run_evaluation_placeholder(payload: GraphRunRequest) -> dict:
    return _placeholder("evaluation_graph", payload)


@router.post("/improvement/run", dependencies=[Depends(require_internal_key)])
async def run_improvement_placeholder(payload: GraphRunRequest) -> dict:
    return _placeholder("improvement_graph", payload)


def _placeholder(name: str, payload: GraphRunRequest) -> dict:
    return {
        "graph_name": name,
        "status": "placeholder",
        "requires_human": False,
        "proposal": payload.proposal,
        "archive_ref": None,
        "messages": [{"node": name, "ok": True, "note": "reserved for next sprint"}],
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
