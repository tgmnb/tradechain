from datetime import date
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api_service.app.api import agent as agent_api
from apps.api_service.app.api.execution_records import create_execution_record
from apps.api_service.app.api.workflows import run_postclose_review
from apps.api_service.app.api.workflows import run_intel_update
from apps.api_service.app.api.workflows import run_major_task
from apps.api_service.app.main import app
from apps.api_service.app.services.internal_clients import internal_clients
from libs.contracts.trading import ExecutionRecordCreateRequest
from libs.db.base import Base
from libs.db.models import EventModel, ReviewModel, TaskModel, TradingPlanModel


@pytest.mark.anyio
async def test_healthz() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_create_task_requires_api_key() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/tasks",
            json={"title": "test task", "type": "major_task", "source": "discord", "chain_type": "major_task"},
        )
    assert response.status_code == 401


# This is an integration skeleton for CI after runtime dependencies are ready.
@pytest.mark.anyio
async def test_intel_update_endpoint_contract_only() -> None:
    class DummySession:
        def commit(self) -> None:
            return None

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key"}

    original_fetch = internal_clients.fetch_mock_events

    async def fake_fetch_mock_events(request, limit: int = 5) -> list[dict]:
        return []

    internal_clients.fetch_mock_events = fake_fetch_mock_events
    try:
        response = await run_intel_update(DummyRequest(), DummySession())
    finally:
        internal_clients.fetch_mock_events = original_fetch
    assert response == {
        "status": "success",
        "ingested": 0,
        "created_events": 0,
        "created_proposals": 0,
    }


@pytest.mark.anyio
async def test_placeholder_workflows_report_current_blockers() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    transport = httpx.ASGITransport(app=app)
    headers = {"X-API-Key": "external-dev-key"}

    try:
        with TestingSessionLocal() as db:
            postclose = await run_postclose_review(DummyRequest(), db=db)

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            nightly = await client.post("/v1/workflows/nightly-improvement/run", headers=headers)
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    assert postclose["status"] == "blocked"
    assert postclose["reason"] == "no_trading_plan"

    assert nightly.status_code == 200
    assert nightly.json()["reason"] == "evaluation_pipeline_required"
    assert "improvement_ticket_skill" in nightly.json()["message"]


@pytest.mark.anyio
async def test_execution_record_api_unblocks_postclose_review() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    plan_id = uuid4()
    strategy_id = uuid4()
    with TestingSessionLocal() as db:
        db.add(
            TradingPlanModel(
                id=plan_id,
                strategy_id=strategy_id,
                plan_date=date(2026, 3, 14),
                title="Test Plan",
                objective="Verify postclose review input path",
                entry_conditions={"items": ["open above range"]},
                exit_conditions={"items": ["close below support"]},
                monitoring_points={"items": ["volume spike"]},
                checklist={"items": ["check proxy"]},
                status="active",
                metadata_json={},
            )
        )
        db.commit()

    async def fake_run_review_graph(request, *, metadata=None, chain_type="postclose_review"):
        return {
            "graph_name": "review_graph",
            "status": "completed",
            "chain_type": chain_type,
            "review": {
                "id": str(uuid4()),
                "trading_plan_id": str(plan_id),
                "task_id": None,
                "reviewer_type": "agent",
                "reviewer_name": "review_graph",
                "decision": "pass",
                "summary": "baseline review completed",
                "deviations": ["one deviation"],
                "issues": ["one issue"],
                "follow_up_actions": ["one follow up"],
                "evidence_summary": {"execution_record_count": 1, "evidence_sources": ["manual"]},
                "score": 80,
                "metadata": metadata or {},
                "created_at": "2026-03-24T00:00:00Z",
            },
        }

    original_run_review_graph = internal_clients.run_review_graph
    internal_clients.run_review_graph = fake_run_review_graph

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    try:
        with TestingSessionLocal() as db:
            created = await create_execution_record(
                ExecutionRecordCreateRequest(
                    trading_plan_id=plan_id,
                    action_type="manual_buy",
                    recorded_by="tester",
                    notes="filled near trigger",
                    result={"price": 101.5, "size": 1},
                ),
                db=db,
            )
            workflow_response = await run_postclose_review(DummyRequest(), db=db)
    finally:
        internal_clients.run_review_graph = original_run_review_graph
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    assert created.action_type == "manual_buy"
    assert created.trading_plan_id == plan_id
    assert created.evidence_source == "manual"

    assert workflow_response["status"] == "success"
    assert workflow_response["execution_record_count"] == 1
    assert workflow_response["review"]["summary"] == "baseline review completed"
    assert workflow_response["review"]["evidence_summary"]["execution_record_count"] == 1
    assert workflow_response["review_id"]
    assert workflow_response["review_graph"]["graph_name"] == "review_graph"


@pytest.mark.anyio
async def test_postclose_review_requires_execution_evidence_when_plan_exists() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add(
            TradingPlanModel(
                id=uuid4(),
                strategy_id=uuid4(),
                plan_date=date(2026, 3, 14),
                title="Evidence Missing Plan",
                objective="Verify blocked path",
                entry_conditions={"items": ["entry"]},
                exit_conditions={"items": ["exit"]},
                monitoring_points={"items": ["monitor"]},
                checklist={"items": ["check"]},
                status="active",
                metadata_json={},
            )
        )
        db.commit()

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    try:
        with TestingSessionLocal() as db:
            response = await run_postclose_review(DummyRequest(), db=db)
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    assert response["status"] == "blocked"
    assert response["reason"] == "execution_records_required"


@pytest.mark.anyio
async def test_gateway_slash_help_and_politburo_chat_split() -> None:
    transport = httpx.ASGITransport(app=app)
    headers = {"X-API-Key": "external-dev-key"}

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        slash_help = await client.post(
            "/v1/agent/discord-message",
            headers=headers,
            json={"text": "/help", "user_name": "tester", "user_id": "1", "channel_id": "1", "guild_id": "1"},
        )
        natural_chat = await client.post(
            "/v1/agent/discord-message",
            headers=headers,
            json={"text": "你是谁", "user_name": "tester", "user_id": "1", "channel_id": "1", "guild_id": "1"},
        )

    assert slash_help.status_code == 200
    assert slash_help.json()["route"] == "help"

    assert natural_chat.status_code == 200
    assert natural_chat.json()["route"] == "help"
    assert "政治局" in natural_chat.json()["summary"]


@pytest.mark.anyio
async def test_politburo_research_query_prefers_web_research() -> None:
    transport = httpx.ASGITransport(app=app)
    headers = {"X-API-Key": "external-dev-key"}

    async def fake_run_web_research_workflow(payload):
        return {
            "status": "success",
            "query": payload.query,
            "result_count": 1,
            "results": [{"title": "Japan policy", "url": "https://example.gov/policy", "excerpt": "Policy text"}],
            "summary": "围绕“日本央行最新政策”做了网页检索。",
        }

    original_run_web_research = agent_api.run_web_research_workflow
    agent_api.run_web_research_workflow = fake_run_web_research_workflow

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/agent/discord-message",
                headers=headers,
                json={
                    "text": "帮我查一下日本央行最新政策",
                    "user_name": "tester",
                    "user_id": "1",
                    "channel_id": "1",
                    "guild_id": "1",
                },
            )
    finally:
        agent_api.run_web_research_workflow = original_run_web_research

    assert response.status_code == 200
    assert response.json()["route"] == "web_research"
    assert "网页检索" in response.json()["summary"]


@pytest.mark.anyio
async def test_major_task_workflow_calls_master_graph_before_planning() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    task_id = uuid4()
    event_id = uuid4()
    proposal_id = uuid4()
    report_id = uuid4()
    strategy_id = uuid4()
    plan_id = uuid4()

    with TestingSessionLocal() as db:
        db.add(
            TaskModel(
                id=task_id,
                title="Launch major task",
                type="major_task",
                source="discord",
                chain_type="major_task",
                priority=50,
                created_by="tester",
                goal_json={"text": "Build a task"},
                context_json={},
            )
        )
        db.add(
            EventModel(
                id=event_id,
                source="mock",
                event_type="macro",
                asset_scope={"assets": ["IF"]},
                title="Macro event",
                content="Event content",
                impact_direction="up",
                confidence=0.8,
                raw_payload={},
                dedup_key="major-task-event",
            )
        )
        db.commit()

    async def fake_run_master_graph(request, *, task=None, proposal=None, metadata=None, chain_type="major_task"):
        return {
            "graph_name": "master_graph",
            "status": "completed",
            "requires_human": False,
            "goal_review": {"decision": "pass"},
            "execution_entry": {"next_stage": "proposal_generation"},
            "task": task,
            "metadata": metadata or {},
        }

    async def fake_run_event_to_proposal_graph(request, *, event, task_id=None, metadata=None, chain_type="major_task"):
        return {
            "proposal": {
                "id": str(proposal_id),
                "task_id": task_id,
                "source_event_id": str(event_id),
                "theme": "Major task theme",
                "asset_scope": ["IF"],
                "initial_logic": "Initial logic",
                "trigger_conditions": ["trigger"],
                "invalidation_conditions": ["invalidate"],
                "risks": ["risk"],
                "confidence": 0.8,
                "status": "draft",
                "recommended_action": "continue_pipeline",
                "requires_human": False,
                "metadata": {},
            }
        }

    async def fake_run_proposal_to_plan_graph(
        request,
        *,
        proposal,
        research_report=None,
        strategy=None,
        task_id=None,
        metadata=None,
        chain_type="major_task",
    ):
        return {
            "research_report": {
                "id": str(report_id),
                "proposal_id": str(proposal_id),
                "task_id": str(task_id),
                "department_id": "state_council",
                "specialist_id": "proposal_officer",
                "title": "Report",
                "summary": "Summary",
                "key_points": ["k1"],
                "risk_points": ["r1"],
                "next_actions": ["n1"],
                "confidence": 0.7,
                "metadata": {},
            },
            "strategy": {
                "id": str(strategy_id),
                "proposal_id": str(proposal_id),
                "research_report_id": str(report_id),
                "task_id": str(task_id),
                "title": "Strategy",
                "thesis": "Thesis",
                "target_assets": ["IF"],
                "setup_conditions": ["setup"],
                "invalidation_conditions": ["invalidate"],
                "risk_controls": ["rc"],
                "status": "draft",
                "priority_score": 60,
                "confidence": 0.7,
                "metadata": {},
            },
            "trading_plan": {
                "id": str(plan_id),
                "strategy_id": str(strategy_id),
                "task_id": str(task_id),
                "plan_date": date(2026, 3, 14).isoformat(),
                "title": "Plan",
                "objective": "Objective",
                "entry_conditions": ["entry"],
                "exit_conditions": ["exit"],
                "monitoring_points": ["monitor"],
                "checklist": ["check"],
                "status": "draft",
                "metadata": {},
            },
        }

    original_master = internal_clients.run_master_graph
    original_event = internal_clients.run_event_to_proposal_graph
    original_plan = internal_clients.run_proposal_to_plan_graph
    internal_clients.run_master_graph = fake_run_master_graph
    internal_clients.run_event_to_proposal_graph = fake_run_event_to_proposal_graph
    internal_clients.run_proposal_to_plan_graph = fake_run_proposal_to_plan_graph

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    try:
        with TestingSessionLocal() as db:
            result = await run_major_task(DummyRequest(), db=db)
        assert result["status"] == "success"
        assert result["task_id"] == str(task_id)
        assert result["master_graph"]["graph_name"] == "master_graph"
        assert result["master_graph"]["status"] == "completed"

        with TestingSessionLocal() as db:
            task = db.get(TaskModel, task_id)
            assert task is not None
            assert task.status == "running"
            assert task.context_json["governance"]["master_graph"]["graph_name"] == "master_graph"
            review = db.scalar(
                select(ReviewModel)
                .where(ReviewModel.object_type == "task")
                .where(ReviewModel.object_id == task_id)
            )
            assert review is not None
            assert review.decision == "pass"
            assert review.reviewer_name == "review_clerk"
    finally:
        internal_clients.run_master_graph = original_master
        internal_clients.run_event_to_proposal_graph = original_event
        internal_clients.run_proposal_to_plan_graph = original_plan
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.anyio
async def test_major_task_stops_when_master_graph_requires_human() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    task_id = uuid4()
    with TestingSessionLocal() as db:
        db.add(
            TaskModel(
                id=task_id,
                title="Blocked major task",
                type="major_task",
                source="discord",
                chain_type="major_task",
                priority=50,
                created_by="tester",
                goal_json={"text": "Need governance review"},
                context_json={},
            )
        )
        db.commit()

    async def fake_run_master_graph(request, *, task=None, proposal=None, metadata=None, chain_type="major_task"):
        return {
            "graph_name": "master_graph",
            "status": "needs_human",
            "requires_human": True,
            "goal_review": {"decision": "reject"},
            "execution_entry": {"next_stage": "goal_revision"},
        }

    original_master = internal_clients.run_master_graph
    internal_clients.run_master_graph = fake_run_master_graph

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    try:
        with TestingSessionLocal() as db:
            result = await run_major_task(DummyRequest(), db=db)
        assert result["status"] == "needs_human"
        assert result["reason"] == "governance_review_required"

        with TestingSessionLocal() as db:
            task = db.get(TaskModel, task_id)
            assert task is not None
            assert task.status == "needs_human"
            assert task.context_json["governance"]["master_graph"]["goal_review"]["decision"] == "reject"
            review = db.scalar(
                select(ReviewModel)
                .where(ReviewModel.object_type == "task")
                .where(ReviewModel.object_id == task_id)
            )
            assert review is not None
            assert review.decision == "reject"
    finally:
        internal_clients.run_master_graph = original_master
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.anyio
async def test_major_task_persists_governance_before_downstream_failure() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    task_id = uuid4()
    event_id = uuid4()
    with TestingSessionLocal() as db:
        db.add(
            TaskModel(
                id=task_id,
                title="Partial major task",
                type="major_task",
                source="discord",
                chain_type="major_task",
                priority=50,
                created_by="tester",
                goal_json={"text": "Persist governance first"},
                context_json={},
            )
        )
        db.add(
            EventModel(
                id=event_id,
                source="mock",
                event_type="macro",
                asset_scope={"assets": ["IF"]},
                title="Macro event",
                content="Event content",
                impact_direction="up",
                confidence=0.8,
                raw_payload={},
                dedup_key="major-task-event-failure",
            )
        )
        db.commit()

    async def fake_run_master_graph(request, *, task=None, proposal=None, metadata=None, chain_type="major_task"):
        return {
            "graph_name": "master_graph",
            "status": "completed",
            "requires_human": False,
            "goal_review": {"decision": "pass", "reason": "Proceed"},
            "execution_entry": {"next_stage": "proposal_generation"},
        }

    async def fake_run_event_to_proposal_graph(request, *, event, task_id=None, metadata=None, chain_type="major_task"):
        raise RuntimeError("downstream proposal graph failed")

    original_master = internal_clients.run_master_graph
    original_event = internal_clients.run_event_to_proposal_graph
    internal_clients.run_master_graph = fake_run_master_graph
    internal_clients.run_event_to_proposal_graph = fake_run_event_to_proposal_graph

    class DummyRequest:
        headers = {"X-API-Key": "external-dev-key", "X-Actor": "test"}

    try:
        with TestingSessionLocal() as db:
            with pytest.raises(RuntimeError, match="downstream proposal graph failed"):
                await run_major_task(DummyRequest(), db=db)

        with TestingSessionLocal() as db:
            task = db.get(TaskModel, task_id)
            assert task is not None
            assert task.status == "running"
            assert task.context_json["governance"]["master_graph"]["goal_review"]["decision"] == "pass"
            review = db.scalar(
                select(ReviewModel)
                .where(ReviewModel.object_type == "task")
                .where(ReviewModel.object_id == task_id)
            )
            assert review is not None
            assert review.decision == "pass"
            assert review.comments == "Proceed"
    finally:
        internal_clients.run_master_graph = original_master
        internal_clients.run_event_to_proposal_graph = original_event
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
