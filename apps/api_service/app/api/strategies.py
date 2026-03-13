from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.runtime_objects import (
    persist_strategy,
    proposal_model_to_payload,
    research_report_model_to_payload,
    strategy_model_to_contract,
)
from apps.api_service.app.services.runtime_profiles import planning_profile_for
from libs.contracts.strategy import Strategy, StrategyDraftRequest
from libs.db.models import ProposalModel, ResearchReportModel, StrategyModel

router = APIRouter(prefix="/v1/strategies", tags=["strategies"], dependencies=[Depends(require_api_key)])


@router.post("/draft", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def draft_strategy(
    payload: StrategyDraftRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Strategy:
    report = db.get(ResearchReportModel, payload.research_report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="research report not found")

    proposal = db.get(ProposalModel, report.proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source proposal not found")

    chain_type = "major_task" if proposal.task_id or payload.task_id else "daily_preopen"
    profile = planning_profile_for(chain_type, department_id=payload.department_id, specialist_id=payload.specialist_id)
    graph_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        research_report=research_report_model_to_payload(report),
        task_id=str(payload.task_id or proposal.task_id) if (payload.task_id or proposal.task_id) else None,
        metadata={**profile, "stop_after": "strategy"},
        chain_type=chain_type,
    )

    strategy_data = graph_result.get("strategy")
    if not strategy_data:
        raise HTTPException(status_code=502, detail="agent-core did not return a strategy")

    strategy = persist_strategy(db, strategy_data)
    db.commit()
    db.refresh(strategy)
    return strategy_model_to_contract(strategy)


@router.get("/latest", response_model=Strategy)
async def get_latest_strategy(db: Session = Depends(get_db)) -> Strategy:
    strategy = db.scalar(select(StrategyModel).order_by(StrategyModel.created_at.desc()))
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="strategy not found")
    return strategy_model_to_contract(strategy)


@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: UUID, db: Session = Depends(get_db)) -> Strategy:
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="strategy not found")
    return strategy_model_to_contract(strategy)
