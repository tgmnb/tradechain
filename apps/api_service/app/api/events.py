from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from libs.contracts.event import EventIn, EventNormalized, build_event_dedup_key
from libs.db.models import EventModel

router = APIRouter(prefix="/v1/events", tags=["events"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=EventNormalized, status_code=status.HTTP_201_CREATED)
async def create_event(payload: EventIn, db: Session = Depends(get_db)) -> EventNormalized:
    dedup_key = build_event_dedup_key(payload)
    existing = db.scalar(select(EventModel).where(EventModel.dedup_key == dedup_key))
    if existing:
        return _to_contract(existing)

    event = EventModel(
        id=uuid4(),
        source=payload.source,
        event_type=payload.event_type,
        title=payload.title,
        content=payload.content,
        asset_scope={"assets": payload.asset_scope},
        impact_direction=payload.impact_direction,
        confidence=payload.confidence,
        raw_payload=payload.raw_payload,
        dedup_key=dedup_key,
        occurred_at=payload.occurred_at,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _to_contract(event)


def _to_contract(event: EventModel) -> EventNormalized:
    confidence = float(event.confidence) if isinstance(event.confidence, Decimal) else float(event.confidence or 0.5)
    return EventNormalized(
        id=event.id,
        source=event.source,
        event_type=event.event_type,
        title=event.title or "",
        content=event.content or "",
        asset_scope=(event.asset_scope or {}).get("assets", []),
        impact_direction=event.impact_direction or "neutral",
        confidence=confidence,
        raw_payload=event.raw_payload or {},
        occurred_at=event.occurred_at,
        dedup_key=event.dedup_key,
        created_at=event.created_at or datetime.now(timezone.utc),
    )
