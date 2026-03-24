from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class AgentScore(ContractModel):
    id: UUID
    agent_name: str = Field(min_length=1, max_length=100)
    period_start: date
    period_end: date
    win_rate: float | None = Field(default=None, ge=0.0, le=100.0)
    precision_score: float | None = Field(default=None, ge=0.0, le=100.0)
    timeliness_score: float | None = Field(default=None, ge=0.0, le=100.0)
    contribution_score: float | None = Field(default=None, ge=0.0, le=100.0)
    stability_score: float | None = Field(default=None, ge=0.0, le=100.0)
    total_score: float | None = Field(default=None, ge=0.0, le=100.0)
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ImprovementTicket(ContractModel):
    id: UUID
    target_type: str = Field(min_length=1, max_length=30)
    target_name: str = Field(min_length=1, max_length=100)
    source_period_start: date | None = None
    source_period_end: date | None = None
    issue_summary: str
    impact_description: str
    root_cause: dict[str, Any] = Field(default_factory=dict)
    proposed_fix: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending_approval", max_length=30)
    approved_by: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    updated_at: datetime
