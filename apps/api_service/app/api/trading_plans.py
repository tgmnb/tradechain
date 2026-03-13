from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.runtime_objects import (
    persist_trading_plan,
    proposal_model_to_payload,
    strategy_model_to_payload,
    trading_plan_model_to_contract,
)
from apps.api_service.app.services.runtime_profiles import planning_profile_for
from libs.contracts.trading import TradingPlan, TradingPlanDraftRequest
from libs.db.models import ProposalModel, StrategyModel, TradingPlanModel

router = APIRouter(prefix="/v1/trading-plans", tags=["trading-plans"], dependencies=[Depends(require_api_key)])


@router.post("/draft", response_model=TradingPlan, status_code=status.HTTP_201_CREATED)
async def draft_trading_plan(
    payload: TradingPlanDraftRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TradingPlan:
    strategy = db.get(StrategyModel, payload.strategy_id)
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="strategy not found")

    proposal = db.get(ProposalModel, strategy.proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source proposal not found")

    chain_type = "major_task" if proposal.task_id or payload.task_id else "daily_preopen"
    profile = planning_profile_for(chain_type, department_id=payload.department_id, specialist_id=payload.specialist_id)
    graph_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        strategy=strategy_model_to_payload(strategy),
        task_id=str(payload.task_id or proposal.task_id) if (payload.task_id or proposal.task_id) else None,
        metadata={
            **profile,
            "stop_after": "trading_plan",
            **({"plan_date": payload.plan_date.isoformat()} if payload.plan_date else {}),
        },
        chain_type=chain_type,
    )

    plan_data = graph_result.get("trading_plan")
    if not plan_data:
        raise HTTPException(status_code=502, detail="agent-core did not return a trading plan")

    plan = persist_trading_plan(db, plan_data)
    db.commit()
    db.refresh(plan)
    return trading_plan_model_to_contract(plan)


@router.get("/latest", response_model=TradingPlan)
async def get_latest_trading_plan(db: Session = Depends(get_db)) -> TradingPlan:
    plan = db.scalar(select(TradingPlanModel).order_by(TradingPlanModel.created_at.desc()))
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trading plan not found")
    return trading_plan_model_to_contract(plan)


@router.get("/{plan_id}", response_model=TradingPlan)
async def get_trading_plan(plan_id: UUID, db: Session = Depends(get_db)) -> TradingPlan:
    plan = db.get(TradingPlanModel, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trading plan not found")
    return trading_plan_model_to_contract(plan)
