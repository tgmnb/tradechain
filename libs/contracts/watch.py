from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class WatchObservation(ContractModel):
    id: UUID
    task_id: UUID | None = None
    chain_type: str = Field(default="intraday_watch", max_length=50)
    asset_scope: list[str] = Field(default_factory=list)
    trigger_type: str = Field(min_length=1, max_length=50)
    severity: str = Field(default="medium", max_length=20)
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    follow_up_action: str = Field(default="notify", max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
