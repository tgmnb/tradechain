from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.runtime_objects import (
    execution_record_model_to_contract,
    persist_execution_record,
)
from libs.contracts.trading import ExecutionRecord, ExecutionRecordCreateRequest
from libs.db.models import ExecutionRecordModel, TradingPlanModel

router = APIRouter(prefix="/v1/execution-records", tags=["execution-records"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=ExecutionRecord, status_code=status.HTTP_201_CREATED)
async def create_execution_record(
    payload: ExecutionRecordCreateRequest,
    db: Session = Depends(get_db),
) -> ExecutionRecord:
    plan = db.get(TradingPlanModel, payload.trading_plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trading plan not found")

    record = persist_execution_record(
        db,
        {
            "id": str(uuid4()),
            "trading_plan_id": str(payload.trading_plan_id),
            "task_id": str(payload.task_id) if payload.task_id else None,
            "action_type": payload.action_type,
            "evidence_source": payload.evidence_source,
            "recorded_by": payload.recorded_by,
            "notes": payload.notes,
            "result": payload.result,
        },
    )
    db.commit()
    db.refresh(record)
    return execution_record_model_to_contract(record)


@router.get("/latest", response_model=ExecutionRecord)
async def get_latest_execution_record(db: Session = Depends(get_db)) -> ExecutionRecord:
    record = db.scalar(select(ExecutionRecordModel).order_by(ExecutionRecordModel.created_at.desc()))
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="execution record not found")
    return execution_record_model_to_contract(record)


@router.get("/by-plan/{plan_id}", response_model=list[ExecutionRecord])
async def list_execution_records_by_plan(plan_id: UUID, db: Session = Depends(get_db)) -> list[ExecutionRecord]:
    records = db.scalars(
        select(ExecutionRecordModel)
        .where(ExecutionRecordModel.trading_plan_id == plan_id)
        .order_by(ExecutionRecordModel.created_at.asc())
    ).all()
    return [execution_record_model_to_contract(record) for record in records]
