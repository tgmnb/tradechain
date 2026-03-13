from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class ResearchReportDraftRequest(ContractModel):
    proposal_id: UUID
    task_id: UUID | None = None
    department_id: str | None = None
    specialist_id: str | None = None


class ResearchReport(ContractModel):
    id: UUID
    proposal_id: UUID
    task_id: UUID | None = None
    department_id: str = Field(min_length=1, max_length=100)
    specialist_id: str | None = Field(default=None, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    summary: str
    key_points: list[str] = Field(default_factory=list)
    risk_points: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    updated_at: datetime
