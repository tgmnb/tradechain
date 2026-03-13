from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class StrategyDraftRequest(ContractModel):
    research_report_id: UUID
    task_id: UUID | None = None
    department_id: str | None = None
    specialist_id: str | None = None


class Strategy(ContractModel):
    id: UUID
    proposal_id: UUID
    research_report_id: UUID
    task_id: UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    thesis: str
    target_assets: list[str] = Field(default_factory=list)
    setup_conditions: list[str] = Field(default_factory=list)
    invalidation_conditions: list[str] = Field(default_factory=list)
    risk_controls: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    priority_score: float = Field(default=50.0, ge=0.0, le=100.0)
    status: str = Field(default="draft", max_length=30)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    updated_at: datetime
