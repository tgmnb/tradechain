from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from libs.contracts.enums import ProposalStatus
from libs.contracts.event import EventNormalized
from libs.contracts.proposal import ProposalDraftRequest, ProposalFinal
from libs.db.models import EventModel, ProposalModel

router = APIRouter(prefix="/v1/proposals", tags=["proposals"], dependencies=[Depends(require_api_key)])


@router.post("/draft", response_model=ProposalFinal, status_code=status.HTTP_201_CREATED)
async def draft_proposal(
    payload: ProposalDraftRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ProposalFinal:
    event = db.get(EventModel, payload.event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")

    event_payload = _event_to_dict(event)
    graph_result = await internal_clients.run_event_to_proposal_graph(
        request=request,
        event=event_payload,
        task_id=str(payload.task_id) if payload.task_id else None,
        metadata={"source": "api_service"},
    )

    proposal_data = graph_result.get("proposal")
    if not proposal_data:
        raise HTTPException(status_code=502, detail="agent-core did not return a proposal")

    proposal = ProposalModel(
        id=UUID(proposal_data["id"]),
        task_id=payload.task_id,
        source_event_id=event.id,
        theme=proposal_data["theme"],
        asset_scope={"assets": proposal_data.get("asset_scope", [])},
        initial_logic=proposal_data["initial_logic"],
        trigger_conditions={"items": proposal_data.get("trigger_conditions", [])},
        invalidation_conditions={"items": proposal_data.get("invalidation_conditions", [])},
        risks={"items": proposal_data.get("risks", [])},
        status=proposal_data.get("status", ProposalStatus.DRAFT),
        rank_score=proposal_data.get("confidence", 0.5) * 100,
        metadata_json=proposal_data.get("metadata", {}),
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return _proposal_to_contract(proposal, proposal_data)


@router.get("/latest", response_model=ProposalFinal)
async def get_latest_proposal(db: Session = Depends(get_db)) -> ProposalFinal:
    proposal = db.scalar(select(ProposalModel).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proposal not found")
    return _proposal_to_contract(proposal)


@router.get("/{proposal_id}", response_model=ProposalFinal)
async def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)) -> ProposalFinal:
    proposal = db.get(ProposalModel, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proposal not found")
    return _proposal_to_contract(proposal)


def _event_to_dict(event: EventModel) -> dict:
    confidence = float(event.confidence) if isinstance(event.confidence, Decimal) else float(event.confidence or 0.5)
    return EventNormalized(
        id=event.id,
        source=event.source,
        event_type=event.event_type,
        title=event.title or "",
        content=event.content or "",
        asset_scope=(event.asset_scope or {}).get("assets", []),
        impact_direction=event.impact_direction or "neutral",
        confidence=confidence,
        raw_payload=event.raw_payload or {},
        occurred_at=event.occurred_at,
        dedup_key=event.dedup_key,
        created_at=event.created_at or datetime.now(timezone.utc),
    ).model_dump(mode="json")


def _proposal_to_contract(proposal: ProposalModel, merged: dict | None = None) -> ProposalFinal:
    merged = merged or {}
    confidence = float(proposal.rank_score or 50) / 100
    return ProposalFinal(
        id=proposal.id,
        task_id=proposal.task_id,
        source_event_id=proposal.source_event_id,
        theme=proposal.theme or "",
        asset_scope=(proposal.asset_scope or {}).get("assets", []),
        initial_logic=proposal.initial_logic or "",
        trigger_conditions=(proposal.trigger_conditions or {}).get("items", []),
        invalidation_conditions=(proposal.invalidation_conditions or {}).get("items", []),
        risks=(proposal.risks or {}).get("items", []),
        confidence=merged.get("confidence", confidence),
        status=merged.get("status", proposal.status),
        recommended_action=merged.get("recommended_action", "wait_for_review"),
        requires_human=merged.get("requires_human", proposal.status == ProposalStatus.PENDING_REVIEW),
        metadata=merged.get("metadata", proposal.metadata_json or {}),
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )
