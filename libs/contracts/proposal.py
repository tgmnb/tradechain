from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel
from libs.contracts.enums import ProposalStatus

SCHEMA_VERSION = "1.0.0"


class ProposalDraftRequest(ContractModel):
    event_id: UUID
    task_id: UUID | None = None
    department_id: str | None = None
    specialist_id: str | None = None


class ProposalDraft(ContractModel):
    id: UUID
    source_event_id: UUID
    task_id: UUID | None = None
    theme: str
    asset_scope: list[str] = Field(default_factory=list)
    initial_logic: str
    trigger_conditions: list[str] = Field(default_factory=list)
    invalidation_conditions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: ProposalStatus = Field(default=ProposalStatus.DRAFT)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
    updated_at: datetime


class ProposalFinal(ProposalDraft):
    recommended_action: str
    requires_human: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProposalDraftFromGraph(ContractModel):
    proposal: ProposalFinal
    archive_ref: dict[str, Any] | None = None
