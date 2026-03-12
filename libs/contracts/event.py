import hashlib
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class EventIn(ContractModel):
    source: str = Field(max_length=100)
    event_type: str = Field(max_length=50)
    title: str = Field(max_length=300)
    content: str
    asset_scope: list[str] = Field(default_factory=list)
    impact_direction: str = Field(default="neutral", max_length=20)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None
    schema_version: str = Field(default=SCHEMA_VERSION)


class EventNormalized(EventIn):
    id: UUID
    dedup_key: str
    created_at: datetime


class IngestionFetchRequest(ContractModel):
    limit: int = Field(default=5, ge=1, le=50)


class IngestionFetchResponse(ContractModel):
    events: list[EventIn]

    @field_validator("events")
    @classmethod
    def non_empty(cls, value: list[EventIn]) -> list[EventIn]:
        if not value:
            raise ValueError("events must not be empty")
        return value


def build_event_dedup_key(event: EventIn) -> str:
    stable = "|".join(
        [
            event.source,
            event.event_type,
            event.title,
            str(event.occurred_at.isoformat() if event.occurred_at else ""),
        ]
    )
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()
