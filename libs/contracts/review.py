from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel
from libs.contracts.enums import ReviewDecision


class ReviewRecord(ContractModel):
    id: UUID
    object_type: str = Field(max_length=30)
    object_id: UUID
    reviewer_type: str = Field(max_length=30)
    reviewer_name: str = Field(max_length=100)
    decision: ReviewDecision
    comments: str | None = None
    score: float | None = Field(default=None, ge=0, le=100)
    created_at: datetime


class PostcloseReview(ContractModel):
    id: UUID
    trading_plan_id: UUID
    task_id: UUID | None = None
    reviewer_type: str = Field(default="agent", max_length=30)
    reviewer_name: str = Field(default="review_graph", max_length=100)
    decision: ReviewDecision
    summary: str
    deviations: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    evidence_summary: dict[str, Any] = Field(default_factory=dict)
    score: float | None = Field(default=None, ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
