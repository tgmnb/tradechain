from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel
from libs.contracts.registry import ResolvedAgentProfile


class GraphState(ContractModel):
    task_id: UUID | None = None
    chain_type: str = "intel_update"
    current_stage: str = "start"
    status: str = "running"
    requires_human: bool = False
    user_goal: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    proposals: list[dict[str, Any]] = Field(default_factory=list)
    reviews: list[dict[str, Any]] = Field(default_factory=list)
    research_reports: list[dict[str, Any]] = Field(default_factory=list)
    strategies: list[dict[str, Any]] = Field(default_factory=list)
    trading_plans: list[dict[str, Any]] = Field(default_factory=list)
    execution_records: list[dict[str, Any]] = Field(default_factory=list)
    archive_refs: list[dict[str, Any]] = Field(default_factory=list)
    scores: dict[str, Any] = Field(default_factory=dict)
    improvement_tickets: list[dict[str, Any]] = Field(default_factory=list)
    messages: list[dict[str, Any]] = Field(default_factory=list)


class GraphRunRequest(ContractModel):
    event: dict[str, Any] | None = None
    proposal: dict[str, Any] | None = None
    research_report: dict[str, Any] | None = None
    strategy: dict[str, Any] | None = None
    task_id: UUID | None = None
    chain_type: str = "intel_update"
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphRunResponse(ContractModel):
    graph_name: str
    status: str
    requires_human: bool = False
    proposal: dict[str, Any] | None = None
    research_report: dict[str, Any] | None = None
    strategy: dict[str, Any] | None = None
    trading_plan: dict[str, Any] | None = None
    execution_record: dict[str, Any] | None = None
    resolved_profile: ResolvedAgentProfile | None = None
    archive_ref: dict[str, Any] | None = None
    archive_refs: list[dict[str, Any]] = Field(default_factory=list)
    messages: list[dict[str, Any]] = Field(default_factory=list)
    finished_at: datetime
