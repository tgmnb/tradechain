from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class DialogueIntent(ContractModel):
    id: UUID
    task_id: UUID
    request_id: str = Field(min_length=1, max_length=100)
    conversation_id: str = Field(min_length=1, max_length=100)
    user_text: str = Field(min_length=1, max_length=4000)
    route: str = Field(min_length=1, max_length=50)
    objective: str = Field(min_length=1, max_length=500)
    topic_scope: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    requested_output: str = Field(default="briefing", max_length=100)
    requires_research: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime


class EvidenceItem(ContractModel):
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=1000)
    source_domain: str = Field(min_length=1, max_length=200)
    source_type: str = Field(default="web", max_length=50)
    trust_level: str = Field(default="medium", max_length=20)
    excerpt: str = Field(default="", max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceBundle(ContractModel):
    id: UUID
    task_id: UUID
    request_id: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=500)
    source_policy: str = Field(default="general", max_length=100)
    rewrite_strategy: str = Field(default="direct", max_length=100)
    items: list[EvidenceItem] = Field(default_factory=list)
    failure_state: str | None = Field(default=None, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime


class ConclusionDraft(ContractModel):
    id: UUID
    task_id: UUID
    request_id: str = Field(min_length=1, max_length=100)
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_action: str = Field(default="notify", max_length=50)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime


class DialogueReply(ContractModel):
    id: UUID
    task_id: UUID
    request_id: str = Field(min_length=1, max_length=100)
    route: str = Field(min_length=1, max_length=50)
    answer_text: str = Field(min_length=1)
    fallback_used: bool = False
    failure_stage: str | None = Field(default=None, max_length=50)
    archive_refs: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime


class DialogueFailureState(ContractModel):
    id: UUID
    task_id: UUID
    request_id: str = Field(min_length=1, max_length=100)
    stage: str = Field(min_length=1, max_length=50)
    cause_category: str = Field(min_length=1, max_length=50)
    fallback_behavior: str = Field(min_length=1, max_length=200)
    retryable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
