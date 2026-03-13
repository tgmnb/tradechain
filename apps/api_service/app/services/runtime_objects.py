from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from libs.contracts.event import EventNormalized
from libs.contracts.proposal import ProposalFinal
from libs.contracts.research import ResearchReport
from libs.contracts.strategy import Strategy
from libs.contracts.trading import TradingPlan
from libs.db.models import EventModel, ProposalModel, ResearchReportModel, StrategyModel, TradingPlanModel



def to_float(value: float | Decimal | None, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    return float(value)



def maybe_uuid(value: str | UUID | None) -> UUID | None:
    if value is None or value == "":
        return None
    return value if isinstance(value, UUID) else UUID(str(value))



def list_payload(value: dict | None, key: str = "items") -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(item) for item in value.get(key, [])]



def event_model_to_payload(event: EventModel) -> dict:
    return EventNormalized(
        id=event.id,
        source=event.source,
        event_type=event.event_type,
        title=event.title or "",
        content=event.content or "",
        asset_scope=(event.asset_scope or {}).get("assets", []),
        impact_direction=event.impact_direction or "neutral",
        confidence=to_float(event.confidence, 0.5),
        raw_payload=event.raw_payload or {},
        occurred_at=event.occurred_at,
        dedup_key=event.dedup_key,
        created_at=event.created_at or datetime.now(timezone.utc),
    ).model_dump(mode="json")



def persist_proposal(
    db: Session,
    proposal_data: dict,
    *,
    source_event_id: UUID | None = None,
    task_id: UUID | None = None,
) -> ProposalModel:
    proposal_id = maybe_uuid(proposal_data["id"])
    if proposal_id is None:
        raise ValueError("proposal id is required")

    proposal = db.get(ProposalModel, proposal_id)
    if not proposal:
        proposal = ProposalModel(id=proposal_id)
        db.add(proposal)

    proposal.task_id = task_id if task_id is not None else maybe_uuid(proposal_data.get("task_id"))
    proposal.source_event_id = source_event_id if source_event_id is not None else maybe_uuid(proposal_data.get("source_event_id"))
    proposal.theme = proposal_data.get("theme")
    proposal.asset_scope = {"assets": proposal_data.get("asset_scope", [])}
    proposal.initial_logic = proposal_data.get("initial_logic")
    proposal.trigger_conditions = {"items": proposal_data.get("trigger_conditions", [])}
    proposal.invalidation_conditions = {"items": proposal_data.get("invalidation_conditions", [])}
    proposal.risks = {"items": proposal_data.get("risks", [])}
    proposal.status = proposal_data.get("status", "draft")
    proposal.rank_score = float(proposal_data.get("confidence", 0.5)) * 100
    proposal.metadata_json = proposal_data.get("metadata", {})
    return proposal



def proposal_model_to_contract(proposal: ProposalModel, merged: dict | None = None) -> ProposalFinal:
    merged = merged or {}
    confidence = to_float(proposal.rank_score, 50.0) / 100
    return ProposalFinal(
        id=proposal.id,
        task_id=proposal.task_id,
        source_event_id=proposal.source_event_id,
        theme=proposal.theme or "",
        asset_scope=(proposal.asset_scope or {}).get("assets", []),
        initial_logic=proposal.initial_logic or "",
        trigger_conditions=list_payload(proposal.trigger_conditions),
        invalidation_conditions=list_payload(proposal.invalidation_conditions),
        risks=list_payload(proposal.risks),
        confidence=merged.get("confidence", confidence),
        status=merged.get("status", proposal.status),
        recommended_action=merged.get("recommended_action", "wait_for_review"),
        requires_human=merged.get("requires_human", proposal.status == "pending_review"),
        metadata=merged.get("metadata", proposal.metadata_json or {}),
        created_at=proposal.created_at or datetime.now(timezone.utc),
        updated_at=proposal.updated_at or datetime.now(timezone.utc),
    )



def proposal_model_to_payload(proposal: ProposalModel, merged: dict | None = None) -> dict:
    return proposal_model_to_contract(proposal, merged).model_dump(mode="json")



def persist_research_report(db: Session, report_data: dict) -> ResearchReportModel:
    report_id = maybe_uuid(report_data["id"])
    if report_id is None:
        raise ValueError("research report id is required")

    report = db.get(ResearchReportModel, report_id)
    if not report:
        report = ResearchReportModel(id=report_id)
        db.add(report)

    report.proposal_id = maybe_uuid(report_data.get("proposal_id"))
    report.task_id = maybe_uuid(report_data.get("task_id"))
    report.department_id = str(report_data.get("department_id", ""))
    report.specialist_id = report_data.get("specialist_id")
    report.title = report_data.get("title")
    report.summary = report_data.get("summary")
    report.key_points = {"items": report_data.get("key_points", [])}
    report.risk_points = {"items": report_data.get("risk_points", [])}
    report.next_actions = {"items": report_data.get("next_actions", [])}
    report.confidence = report_data.get("confidence", 0.5)
    report.metadata_json = report_data.get("metadata", {})
    return report



def research_report_model_to_contract(report: ResearchReportModel) -> ResearchReport:
    return ResearchReport(
        id=report.id,
        proposal_id=report.proposal_id,
        task_id=report.task_id,
        department_id=report.department_id,
        specialist_id=report.specialist_id,
        title=report.title or "",
        summary=report.summary or "",
        key_points=list_payload(report.key_points),
        risk_points=list_payload(report.risk_points),
        next_actions=list_payload(report.next_actions),
        confidence=to_float(report.confidence, 0.5),
        metadata=report.metadata_json or {},
        created_at=report.created_at or datetime.now(timezone.utc),
        updated_at=report.updated_at or datetime.now(timezone.utc),
    )



def research_report_model_to_payload(report: ResearchReportModel) -> dict:
    return research_report_model_to_contract(report).model_dump(mode="json")



def persist_strategy(db: Session, strategy_data: dict) -> StrategyModel:
    strategy_id = maybe_uuid(strategy_data["id"])
    if strategy_id is None:
        raise ValueError("strategy id is required")

    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        strategy = StrategyModel(id=strategy_id)
        db.add(strategy)

    strategy.proposal_id = maybe_uuid(strategy_data.get("proposal_id"))
    strategy.research_report_id = maybe_uuid(strategy_data.get("research_report_id"))
    strategy.task_id = maybe_uuid(strategy_data.get("task_id"))
    strategy.title = strategy_data.get("title")
    strategy.thesis = strategy_data.get("thesis")
    strategy.target_assets = {"items": strategy_data.get("target_assets", [])}
    strategy.setup_conditions = {"items": strategy_data.get("setup_conditions", [])}
    strategy.invalidation_conditions = {"items": strategy_data.get("invalidation_conditions", [])}
    strategy.risk_controls = {"items": strategy_data.get("risk_controls", [])}
    strategy.status = strategy_data.get("status", "draft")
    strategy.priority_score = strategy_data.get("priority_score", 50)
    strategy.confidence = strategy_data.get("confidence", 0.5)
    strategy.metadata_json = strategy_data.get("metadata", {})
    return strategy



def strategy_model_to_contract(strategy: StrategyModel) -> Strategy:
    return Strategy(
        id=strategy.id,
        proposal_id=strategy.proposal_id,
        research_report_id=strategy.research_report_id,
        task_id=strategy.task_id,
        title=strategy.title or "",
        thesis=strategy.thesis or "",
        target_assets=list_payload(strategy.target_assets),
        setup_conditions=list_payload(strategy.setup_conditions),
        invalidation_conditions=list_payload(strategy.invalidation_conditions),
        risk_controls=list_payload(strategy.risk_controls),
        confidence=to_float(strategy.confidence, 0.5),
        priority_score=to_float(strategy.priority_score, 50.0),
        status=strategy.status,
        metadata=strategy.metadata_json or {},
        created_at=strategy.created_at or datetime.now(timezone.utc),
        updated_at=strategy.updated_at or datetime.now(timezone.utc),
    )



def strategy_model_to_payload(strategy: StrategyModel) -> dict:
    return strategy_model_to_contract(strategy).model_dump(mode="json")



def persist_trading_plan(db: Session, plan_data: dict) -> TradingPlanModel:
    plan_id = maybe_uuid(plan_data["id"])
    if plan_id is None:
        raise ValueError("trading plan id is required")

    plan = db.get(TradingPlanModel, plan_id)
    if not plan:
        plan = TradingPlanModel(id=plan_id)
        db.add(plan)

    plan.strategy_id = maybe_uuid(plan_data.get("strategy_id"))
    plan.task_id = maybe_uuid(plan_data.get("task_id"))
    plan.plan_date = plan_data.get("plan_date") if isinstance(plan_data.get("plan_date"), date) else date.fromisoformat(str(plan_data.get("plan_date")))
    plan.title = plan_data.get("title")
    plan.objective = plan_data.get("objective")
    plan.entry_conditions = {"items": plan_data.get("entry_conditions", [])}
    plan.exit_conditions = {"items": plan_data.get("exit_conditions", [])}
    plan.monitoring_points = {"items": plan_data.get("monitoring_points", [])}
    plan.checklist = {"items": plan_data.get("checklist", [])}
    plan.status = plan_data.get("status", "draft")
    plan.metadata_json = plan_data.get("metadata", {})
    return plan



def trading_plan_model_to_contract(plan: TradingPlanModel) -> TradingPlan:
    return TradingPlan(
        id=plan.id,
        strategy_id=plan.strategy_id,
        task_id=plan.task_id,
        plan_date=plan.plan_date,
        title=plan.title or "",
        objective=plan.objective or "",
        entry_conditions=list_payload(plan.entry_conditions),
        exit_conditions=list_payload(plan.exit_conditions),
        monitoring_points=list_payload(plan.monitoring_points),
        checklist=list_payload(plan.checklist),
        status=plan.status,
        metadata=plan.metadata_json or {},
        created_at=plan.created_at or datetime.now(timezone.utc),
        updated_at=plan.updated_at or datetime.now(timezone.utc),
    )



def trading_plan_model_to_payload(plan: TradingPlanModel) -> dict:
    return trading_plan_model_to_contract(plan).model_dump(mode="json")
