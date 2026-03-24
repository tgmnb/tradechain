from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.runtime_objects import (
    agent_score_model_to_contract,
    improvement_ticket_model_to_contract,
)
from libs.contracts.improvement import AgentScore, ImprovementTicket
from libs.db.models import AgentScoreModel, ImprovementTicketModel

router = APIRouter(prefix="/v1/improvement", tags=["improvement"], dependencies=[Depends(require_api_key)])


@router.get("/scores/latest", response_model=AgentScore)
async def get_latest_agent_score(db: Session = Depends(get_db)) -> AgentScore:
    score = db.scalar(select(AgentScoreModel).order_by(AgentScoreModel.created_at.desc()))
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent score not found")
    return agent_score_model_to_contract(score)


@router.get("/scores/by-agent/{agent_name}", response_model=list[AgentScore])
async def list_agent_scores(agent_name: str, db: Session = Depends(get_db)) -> list[AgentScore]:
    scores = db.scalars(
        select(AgentScoreModel)
        .where(AgentScoreModel.agent_name == agent_name)
        .order_by(AgentScoreModel.period_start.desc(), AgentScoreModel.created_at.desc())
    ).all()
    return [agent_score_model_to_contract(score) for score in scores]


@router.get("/tickets/latest", response_model=ImprovementTicket)
async def get_latest_improvement_ticket(db: Session = Depends(get_db)) -> ImprovementTicket:
    ticket = db.scalar(select(ImprovementTicketModel).order_by(ImprovementTicketModel.created_at.desc()))
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="improvement ticket not found")
    return improvement_ticket_model_to_contract(ticket)


@router.get("/tickets/by-target/{target_type}/{target_name}", response_model=list[ImprovementTicket])
async def list_improvement_tickets(target_type: str, target_name: str, db: Session = Depends(get_db)) -> list[ImprovementTicket]:
    tickets = db.scalars(
        select(ImprovementTicketModel)
        .where(ImprovementTicketModel.target_type == target_type)
        .where(ImprovementTicketModel.target_name == target_name)
        .order_by(ImprovementTicketModel.created_at.desc())
    ).all()
    return [improvement_ticket_model_to_contract(ticket) for ticket in tickets]
