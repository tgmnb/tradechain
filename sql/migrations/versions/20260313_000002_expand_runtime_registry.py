"""expand runtime registry and planning tables"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260313_000002"
down_revision: Union[str, Sequence[str], None] = "20260312_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "soul_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("soul_id", sa.String(length=100), nullable=False),
        sa.Column("soul_type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department_id", sa.String(length=100), nullable=True),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("manifest", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "research_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proposals.id"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("department_id", sa.String(length=100), nullable=False),
        sa.Column("specialist_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_points", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risk_points", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("next_actions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proposals.id"), nullable=False),
        sa.Column("research_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_reports.id"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("target_assets", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("setup_conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("invalidation_conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risk_controls", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("priority_score", sa.Numeric(8, 2), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "trading_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("entry_conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("exit_conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("monitoring_points", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("checklist", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "execution_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("trading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trading_plans.id"), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("recorded_by", sa.String(length=100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "agent_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("win_rate", sa.Numeric(6, 2), nullable=True),
        sa.Column("precision_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("timeliness_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("contribution_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("stability_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("total_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("detail_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_table(
        "improvement_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=False),
        sa.Column("target_name", sa.String(length=100), nullable=False),
        sa.Column("source_period_start", sa.Date(), nullable=True),
        sa.Column("source_period_end", sa.Date(), nullable=True),
        sa.Column("issue_summary", sa.Text(), nullable=True),
        sa.Column("impact_description", sa.Text(), nullable=True),
        sa.Column("root_cause", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("proposed_fix", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    op.create_index("idx_soul_versions_soul_version", "soul_versions", ["soul_id", "version"])
    op.create_index("idx_research_reports_proposal", "research_reports", ["proposal_id"])
    op.create_index("idx_strategies_report", "strategies", ["research_report_id"])
    op.create_index("idx_trading_plans_strategy", "trading_plans", ["strategy_id"])
    op.create_index("idx_execution_records_plan", "execution_records", ["trading_plan_id"])
    op.create_index("idx_agent_scores_agent_period", "agent_scores", ["agent_name", "period_start", "period_end"])
    op.create_index("idx_improvement_tickets_target_status", "improvement_tickets", ["target_type", "status"])


def downgrade() -> None:
    op.drop_index("idx_improvement_tickets_target_status", table_name="improvement_tickets")
    op.drop_index("idx_agent_scores_agent_period", table_name="agent_scores")
    op.drop_index("idx_execution_records_plan", table_name="execution_records")
    op.drop_index("idx_trading_plans_strategy", table_name="trading_plans")
    op.drop_index("idx_strategies_report", table_name="strategies")
    op.drop_index("idx_research_reports_proposal", table_name="research_reports")
    op.drop_index("idx_soul_versions_soul_version", table_name="soul_versions")

    op.drop_table("improvement_tickets")
    op.drop_table("agent_scores")
    op.drop_table("execution_records")
    op.drop_table("trading_plans")
    op.drop_table("strategies")
    op.drop_table("research_reports")
    op.drop_table("soul_versions")
