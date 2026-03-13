from datetime import date, datetime, timezone
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from libs.db.base import Base



def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=50)
    chain_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    goal_json: Mapped[dict] = mapped_column(JSON, default=dict)
    context_json: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_human: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    dedup_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ProposalModel(Base):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id"), nullable=True
    )
    theme: Mapped[str | None] = mapped_column(String(200), nullable=True)
    asset_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    initial_logic: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    invalidation_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    risks: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    rank_score: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_type: Mapped[str] = mapped_column(String(30), nullable=False)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reviewer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reviewer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ArchiveModel(Base):
    __tablename__ = "archives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    archive_key: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(30), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SkillVersionModel(Base):
    __tablename__ = "skill_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    owner_department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSON, default=dict)
    test_result: Mapped[dict] = mapped_column(JSON, default=dict)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SoulVersionModel(Base):
    __tablename__ = "soul_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    soul_id: Mapped[str] = mapped_column(String(100), nullable=False)
    soul_type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSON, default=dict)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ResearchReportModel(Base):
    __tablename__ = "research_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    proposal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    department_id: Mapped[str] = mapped_column(String(100), nullable=False)
    specialist_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_points: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_points: Mapped[dict] = mapped_column(JSON, default=dict)
    next_actions: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class StrategyModel(Base):
    __tablename__ = "strategies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    proposal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False)
    research_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_reports.id"), nullable=False
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_assets: Mapped[dict] = mapped_column(JSON, default=dict)
    setup_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    invalidation_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_controls: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    priority_score: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class TradingPlanModel(Base):
    __tablename__ = "trading_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    strategy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    entry_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    exit_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    monitoring_points: Mapped[dict] = mapped_column(JSON, default=dict)
    checklist: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class ExecutionRecordModel(Base):
    __tablename__ = "execution_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trading_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trading_plans.id"), nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    recorded_by: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AgentScoreModel(Base):
    __tablename__ = "agent_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    win_rate: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    precision_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    timeliness_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    contribution_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    stability_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    total_score: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    detail_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ImprovementTicketModel(Base):
    __tablename__ = "improvement_tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    issue_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[dict] = mapped_column(JSON, default=dict)
    proposed_fix: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


Index("idx_tasks_chain_status", TaskModel.chain_type, TaskModel.status)
Index("idx_events_occurred_at", EventModel.occurred_at)
Index("idx_proposals_status", ProposalModel.status)
Index("idx_archives_object", ArchiveModel.object_type, ArchiveModel.object_id)
Index("idx_skill_versions_name_version", SkillVersionModel.skill_name, SkillVersionModel.version)
Index("idx_soul_versions_soul_version", SoulVersionModel.soul_id, SoulVersionModel.version)
Index("idx_research_reports_proposal", ResearchReportModel.proposal_id)
Index("idx_strategies_report", StrategyModel.research_report_id)
Index("idx_trading_plans_strategy", TradingPlanModel.strategy_id)
Index("idx_execution_records_plan", ExecutionRecordModel.trading_plan_id)
Index("idx_agent_scores_agent_period", AgentScoreModel.agent_name, AgentScoreModel.period_start, AgentScoreModel.period_end)
Index("idx_improvement_tickets_target_status", ImprovementTicketModel.target_type, ImprovementTicketModel.status)
