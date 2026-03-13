from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.runtime_objects import (
    event_model_to_payload,
    persist_proposal,
    persist_research_report,
    persist_strategy,
    persist_trading_plan,
    proposal_model_to_payload,
)
from apps.api_service.app.services.runtime_profiles import planning_profile_for, proposal_profile_for
from libs.contracts.event import EventIn, build_event_dedup_key
from libs.db.models import EventModel, ProposalModel, TaskModel

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
            event=event_model_to_payload(event),
            task_id=None,
            metadata={
                **proposal_profile_for("intel_update"),
                "source": "workflow_intel_update",
            },
            chain_type="intel_update",
        )

        proposal_data = graph_result.get("proposal")
        proposal_id = UUID(str(proposal_data["id"])) if proposal_data else None
        if proposal_data and proposal_id and not db.get(ProposalModel, proposal_id):
            persist_proposal(db, proposal_data, source_event_id=event.id)
            created_proposals += 1

    db.commit()
    return {
        "status": "success",
        "ingested": len(events),
        "created_events": created_events,
        "created_proposals": created_proposals,
    }


@router.post("/major-task/run")
async def run_major_task(request: Request, db: Session = Depends(get_db)) -> dict:
    task = db.scalar(select(TaskModel).where(TaskModel.chain_type == "major_task").order_by(TaskModel.created_at.desc()))
    if not task:
        return {
            "status": "blocked",
            "reason": "no_major_task",
            "message": "Create a major_task first before running this workflow.",
        }

    proposal = db.scalar(select(ProposalModel).where(ProposalModel.task_id == task.id).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        event = db.scalar(select(EventModel).order_by(EventModel.created_at.desc()))
        if not event:
            return {
                "status": "blocked",
                "reason": "no_event_context",
                "message": "No event is available to draft a proposal for the latest major task.",
            }

        proposal_result = await internal_clients.run_event_to_proposal_graph(
            request=request,
            event=event_model_to_payload(event),
            task_id=str(task.id),
            metadata={
                **proposal_profile_for("major_task"),
                "source": "workflow_major_task",
            },
            chain_type="major_task",
        )
        proposal_data = proposal_result.get("proposal")
        if not proposal_data:
            return {
                "status": "failed",
                "reason": "proposal_generation_failed",
                "message": "agent-core did not return a proposal for the latest major task.",
            }
        proposal = persist_proposal(db, proposal_data, task_id=task.id, source_event_id=event.id)
        db.flush()

    plan_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        task_id=str(task.id),
        metadata={
            **planning_profile_for("major_task"),
            "stop_after": "trading_plan",
            "plan_date": date.today().isoformat(),
        },
        chain_type="major_task",
    )

    report_data = plan_result.get("research_report")
    strategy_data = plan_result.get("strategy")
    plan_data = plan_result.get("trading_plan")
    if not (report_data and strategy_data and plan_data):
        return {
            "status": "failed",
            "reason": "planning_pipeline_failed",
            "message": "agent-core did not return the full research -> strategy -> plan chain.",
        }

    report = persist_research_report(db, report_data)
    strategy = persist_strategy(db, strategy_data)
    plan = persist_trading_plan(db, plan_data)
    db.commit()
    db.refresh(report)
    db.refresh(strategy)
    db.refresh(plan)

    return {
        "status": "success",
        "task_id": str(task.id),
        "proposal_id": str(proposal.id),
        "research_report_id": str(report.id),
        "strategy_id": str(strategy.id),
        "trading_plan_id": str(plan.id),
    }


@router.post("/daily-preopen/run")
async def run_daily_preopen(request: Request, db: Session = Depends(get_db)) -> dict:
    proposal = db.scalar(select(ProposalModel).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        return {
            "status": "blocked",
            "reason": "no_proposal",
            "message": "Run intel-update or draft a proposal before daily-preopen.",
        }

    plan_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        task_id=str(proposal.task_id) if proposal.task_id else None,
        metadata={
            **planning_profile_for("daily_preopen"),
            "stop_after": "trading_plan",
            "plan_date": date.today().isoformat(),
        },
        chain_type="daily_preopen",
    )

    report_data = plan_result.get("research_report")
    strategy_data = plan_result.get("strategy")
    plan_data = plan_result.get("trading_plan")
    if not (report_data and strategy_data and plan_data):
        return {
            "status": "failed",
            "reason": "planning_pipeline_failed",
            "message": "agent-core did not return the full daily-preopen planning chain.",
        }

    report = persist_research_report(db, report_data)
    strategy = persist_strategy(db, strategy_data)
    plan = persist_trading_plan(db, plan_data)
    db.commit()
    db.refresh(report)
    db.refresh(strategy)
    db.refresh(plan)

    return {
        "status": "success",
        "proposal_id": str(proposal.id),
        "research_report_id": str(report.id),
        "strategy_id": str(strategy.id),
        "trading_plan_id": str(plan.id),
        "plan_date": plan.plan_date.isoformat(),
    }


@router.post("/intraday-watch/run")
async def run_intraday_watch_placeholder() -> dict:
    return {
        "status": "blocked",
        "reason": "live_market_data_required",
        "message": "intraday-watch needs live market data, plan triggers, and deployment-side scheduling.",
    }


@router.post("/postclose-review/run")
async def run_postclose_review_placeholder() -> dict:
    return {
        "status": "blocked",
        "reason": "execution_records_required",
        "message": "postclose-review needs execution records and plan-vs-action comparison before it can run.",
    }


@router.post("/nightly-improvement/run")
async def run_nightly_improvement_placeholder() -> dict:
    return {
        "status": "blocked",
        "reason": "evaluation_pipeline_required",
        "message": "nightly-improvement needs evaluation signals, scores, and approval workflow before it can run.",
    }
