from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel
from libs.contracts.enums import TaskStatus


class TaskCreate(ContractModel):
    title: str = Field(min_length=3, max_length=200)
    type: str = Field(default="major_task", max_length=50)
    source: str = Field(default="discord", max_length=50)
    chain_type: str = Field(default="major_task", max_length=50)
    priority: int = Field(default=50, ge=0, le=100)
    goal_json: dict[str, Any] = Field(default_factory=dict)
    context_json: dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(default="user")


class TaskRead(ContractModel):
    id: UUID
    title: str
    type: str
    source: str | None = None
    status: TaskStatus
    priority: int
    chain_type: str
    created_by: str | None = None
    requires_human: bool = False
    goal_json: dict[str, Any] = Field(default_factory=dict)
    context_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
