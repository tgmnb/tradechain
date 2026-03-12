from datetime import datetime
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
