from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from libs.contracts.event import EventIn, EventNormalized, build_event_dedup_key
from libs.db.models import EventModel

router = APIRouter(prefix="/v1/workflows", tags=["workflows"], dependencies=[Depends(require_api_key)])


@router.post("/intel-update/run")
async def run_intel_update(request: Request, db: Session = Depends(get_db)) -> dict:
    events = await internal_clients.fetch_mock_events(request, limit=5)

    created_events = 0
    created_proposals = 0

    for item in events:
        payload = EventIn.model_validate(item)
        dedup_key = build_event_dedup_key(payload)

        event = db.scalar(select(EventModel).where(EventModel.dedup_key == dedup_key))
        if not event:
            event = EventModel(
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
            db.flush()
            created_events += 1

        graph_result = await internal_clients.run_event_to_proposal_graph(
            request=request,
            event=_event_to_payload(event),
            task_id=None,
            metadata={"source": "workflow_intel_update"},
        )

        proposal_data = graph_result.get("proposal")
        if proposal_data:
            from libs.db.models import ProposalModel
            from uuid import UUID

            existing_proposal = db.get(ProposalModel, UUID(proposal_data["id"]))
            if not existing_proposal:
                proposal = ProposalModel(
                    id=UUID(proposal_data["id"]),
                    source_event_id=event.id,
                    theme=proposal_data["theme"],
                    asset_scope={"assets": proposal_data.get("asset_scope", [])},
                    initial_logic=proposal_data["initial_logic"],
                    trigger_conditions={"items": proposal_data.get("trigger_conditions", [])},
                    invalidation_conditions={"items": proposal_data.get("invalidation_conditions", [])},
                    risks={"items": proposal_data.get("risks", [])},
                    status=proposal_data.get("status", "draft"),
                    rank_score=proposal_data.get("confidence", 0.5) * 100,
                    metadata_json=proposal_data.get("metadata", {}),
                )
                db.add(proposal)
                created_proposals += 1

    db.commit()
    return {
        "status": "success",
        "ingested": len(events),
        "created_events": created_events,
        "created_proposals": created_proposals,
    }


@router.post("/major-task/run")
async def run_major_task_placeholder() -> dict:
    return {"status": "placeholder", "message": "major-task workflow reserved for Sprint 3+"}


@router.post("/daily-preopen/run")
async def run_daily_preopen_placeholder() -> dict:
    return {"status": "placeholder", "message": "daily-preopen workflow reserved for Sprint 3+"}


@router.post("/intraday-watch/run")
async def run_intraday_watch_placeholder() -> dict:
    return {"status": "placeholder", "message": "intraday-watch workflow reserved for Sprint 4+"}


@router.post("/postclose-review/run")
async def run_postclose_review_placeholder() -> dict:
    return {"status": "placeholder", "message": "postclose-review workflow reserved for Sprint 5+"}


@router.post("/nightly-improvement/run")
async def run_nightly_improvement_placeholder() -> dict:
    return {"status": "placeholder", "message": "nightly-improvement workflow reserved for Sprint 6+"}


def _event_to_payload(event: EventModel) -> dict:
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
    ).model_dump(mode="json")
