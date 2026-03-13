from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.runtime_objects import (
    event_model_to_payload,
    persist_proposal,
    proposal_model_to_contract,
)
from apps.api_service.app.services.runtime_profiles import proposal_profile_for
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

    chain_type = "major_task" if payload.task_id else "intel_update"
    profile = proposal_profile_for(
        chain_type,
        department_id=payload.department_id,
        specialist_id=payload.specialist_id,
    )
    graph_result = await internal_clients.run_event_to_proposal_graph(
        request=request,
        event=event_model_to_payload(event),
        task_id=str(payload.task_id) if payload.task_id else None,
        metadata=profile,
        chain_type=chain_type,
    )

    proposal_data = graph_result.get("proposal")
    if not proposal_data:
        raise HTTPException(status_code=502, detail="agent-core did not return a proposal")

    proposal = persist_proposal(db, proposal_data, source_event_id=event.id, task_id=payload.task_id)
    db.commit()
    db.refresh(proposal)

    return proposal_model_to_contract(proposal, proposal_data)


@router.get("/latest", response_model=ProposalFinal)
async def get_latest_proposal(db: Session = Depends(get_db)) -> ProposalFinal:
    proposal = db.scalar(select(ProposalModel).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proposal not found")
    return proposal_model_to_contract(proposal)


@router.get("/{proposal_id}", response_model=ProposalFinal)
async def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)) -> ProposalFinal:
    proposal = db.get(ProposalModel, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proposal not found")
    return proposal_model_to_contract(proposal)
