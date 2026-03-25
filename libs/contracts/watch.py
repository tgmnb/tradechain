from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel

SCHEMA_VERSION = "1.0.0"


class MarketSnapshot(ContractModel):
    asset: str = Field(min_length=1, max_length=100)
    observed_at: datetime
    last_price: float = Field(gt=0)
    prev_close: float = Field(gt=0)
    session_high: float = Field(gt=0)
    session_low: float = Field(gt=0)
    volume: float = Field(ge=0)
    average_volume: float = Field(gt=0)
    source: str = Field(default="mock_replay", max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntradayWatchRequest(ContractModel):
    input_mode: str = Field(default="mock_replay", max_length=50)
    snapshots: list[MarketSnapshot] = Field(default_factory=list)
    price_change_threshold_pct: float = Field(default=2.0, gt=0)
    session_range_threshold_pct: float = Field(default=3.0, gt=0)
    volume_spike_ratio: float = Field(default=2.0, gt=0)
    suppression_window_minutes: int = Field(default=15, ge=1, le=240)
    routing_targets: list[str] = Field(default_factory=lambda: ["discord", "n8n"])
    metadata: dict[str, Any] = Field(default_factory=dict)


class WatchObservation(ContractModel):
    id: UUID
    task_id: UUID | None = None
    chain_type: str = Field(default="intraday_watch", max_length=50)
    asset_scope: list[str] = Field(default_factory=list)
    source: str = Field(default="mock_replay", max_length=50)
    observed_at: datetime
    trigger_type: str = Field(min_length=1, max_length=50)
    severity: str = Field(default="medium", max_length=20)
    summary: str
    dedup_key: str = Field(min_length=1, max_length=200)
    evidence: dict[str, Any] = Field(default_factory=dict)
    follow_up_action: str = Field(default="notify", max_length=50)
    routing_targets: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION)
    created_at: datetime
