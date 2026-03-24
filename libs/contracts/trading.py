from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class TradingPlanDraftRequest(ContractModel):
    strategy_id: UUID
    task_id: UUID | None = None
    plan_date: date | None = None
    department_id: str | None = None
    specialist_id: str | None = None


class TradingPlan(ContractModel):
    id: UUID
    strategy_id: UUID
    task_id: UUID | None = None
    plan_date: date
    title: str = Field(min_length=1, max_length=200)
    objective: str
    entry_conditions: list[str] = Field(default_factory=list)
    exit_conditions: list[str] = Field(default_factory=list)
    monitoring_points: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    status: str = Field(default="draft", max_length=30)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    updated_at: datetime


class ExecutionRecordCreateRequest(ContractModel):
    trading_plan_id: UUID
    task_id: UUID | None = None
    action_type: str = Field(min_length=1, max_length=50)
    evidence_source: str = Field(default="manual", min_length=1, max_length=50)
    recorded_by: str = Field(min_length=1, max_length=100)
    notes: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)


class ExecutionRecord(ContractModel):
    id: UUID
    trading_plan_id: UUID
    task_id: UUID | None = None
    action_type: str = Field(min_length=1, max_length=50)
    evidence_source: str = Field(default="manual", min_length=1, max_length=50)
    recorded_by: str = Field(min_length=1, max_length=100)
    notes: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
