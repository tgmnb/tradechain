from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status

from apps.agent_core.app.graphs.event_to_proposal import build_event_to_proposal_graph
from apps.agent_core.app.graphs.proposal_to_plan import build_proposal_to_plan_graph
from libs.contracts.graph import GraphRunRequest, GraphRunResponse

router = APIRouter(prefix="/internal/graphs", tags=["graphs"])
event_to_proposal_graph = build_event_to_proposal_graph()
proposal_to_plan_graph = build_proposal_to_plan_graph()



def require_internal_key(x_api_key: str | None = Header(default=None)) -> None:
    from os import getenv

    expected = getenv("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal API key")



def _last_archive_ref(result: dict) -> dict | None:
    archive_refs = result.get("archive_refs") or []
    return archive_refs[-1] if archive_refs else result.get("archive_ref")


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
        "graph_name": "event_to_proposal_graph",
        "messages": [],
    }
    result = event_to_proposal_graph.invoke(state)
    proposal = result.get("proposal")
    if not proposal:
        return GraphRunResponse(
            graph_name="event_to_proposal_graph",
            status="failed",
            requires_human=False,
            proposal=None,
            resolved_profile=result.get("resolved_profile"),
            archive_ref=result.get("archive_ref"),
            archive_refs=result.get("archive_refs", []),
            messages=result.get("messages", []),
            finished_at=datetime.now(timezone.utc),
        )

    return GraphRunResponse(
        graph_name="event_to_proposal_graph",
        status="needs_human" if proposal.get("requires_human") else "completed",
        requires_human=proposal.get("requires_human", False),
        proposal=proposal,
        resolved_profile=result.get("resolved_profile"),
        archive_ref=result.get("archive_ref"),
        archive_refs=result.get("archive_refs", []),
        messages=result.get("messages", []),
        finished_at=datetime.now(timezone.utc),
    )


@router.post("/proposal-to-plan/run", response_model=GraphRunResponse, dependencies=[Depends(require_internal_key)])
async def run_proposal_to_plan(
    payload: GraphRunRequest,
    x_request_id: str | None = Header(default=None),
    x_chain_type: str | None = Header(default="daily_preopen"),
    x_actor: str | None = Header(default="api-service"),
) -> GraphRunResponse:
    if not payload.proposal:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="proposal is required")

    stop_after = payload.metadata.get("stop_after", "trading_plan")
    state = {
        "task_id": str(payload.task_id) if payload.task_id else payload.proposal.get("task_id"),
        "chain_type": payload.chain_type or x_chain_type or "daily_preopen",
        "proposal": payload.proposal,
        "research_report": payload.research_report,
        "strategy": payload.strategy,
        "metadata": payload.metadata,
        "request_id": x_request_id or str(uuid4()),
        "actor": x_actor,
        "graph_name": "proposal_to_plan_graph",
        "stop_after": stop_after,
        "messages": [],
    }
    result = proposal_to_plan_graph.invoke(state)

    status_value = "completed"
    if stop_after == "research" and not result.get("research_report"):
        status_value = "failed"
    if stop_after == "strategy" and not result.get("strategy"):
        status_value = "failed"
    if stop_after == "trading_plan" and not result.get("trading_plan"):
        status_value = "failed"

    return GraphRunResponse(
        graph_name="proposal_to_plan_graph",
        status=status_value,
        requires_human=False,
        proposal=result.get("proposal") or payload.proposal,
        research_report=result.get("research_report") or payload.research_report,
        strategy=result.get("strategy") or payload.strategy,
        trading_plan=result.get("trading_plan"),
        resolved_profile=result.get("resolved_profile"),
        archive_ref=_last_archive_ref(result),
        archive_refs=result.get("archive_refs", []),
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
