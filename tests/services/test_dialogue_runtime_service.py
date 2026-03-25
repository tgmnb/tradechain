from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api_service.app.services.dialogue_runtime_service import dialogue_runtime_service
from libs.db.base import Base
from libs.db.models import TaskModel


def test_dialogue_runtime_creates_task_and_intent() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    try:
        with testing_session_local() as db:
            task, intent = dialogue_runtime_service.create_dialogue_task(
                db,
                payload={
                    "text": "你研究一下，美国的加降息情况",
                    "user_name": "tester",
                    "channel_id": "chan-1",
                    "guild_id": "guild-1",
                    "conversation_id": "conv-1",
                    "request_id": "req-1",
                    "topic_scope": ["macro", "rates"],
                    "constraints": ["answer in Chinese"],
                },
                route="governed_dialogue",
                objective="Assess the current US rate hike/rate cut stance",
                requires_research=True,
            )
            persisted = db.get(TaskModel, task.id)
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    assert persisted is not None
    assert persisted.chain_type == "direct_dialogue"
    assert intent.task_id == task.id
    assert intent.request_id == "req-1"
    assert intent.requires_research is True
    assert intent.topic_scope == ["macro", "rates"]


def test_dialogue_runtime_builds_conclusion_reply_and_failure() -> None:
    task_id = uuid4()
    request_id = "req-2"

    conclusion = dialogue_runtime_service.build_conclusion(
        task_id=task_id,
        request_id=request_id,
        summary="The Fed remains cautious and data-dependent.",
        key_points=["Inflation progress has slowed", "Cuts are not imminent"],
        evidence_refs=["https://www.federalreserve.gov/monetarypolicy.htm"],
    )
    reply = dialogue_runtime_service.build_reply(
        task_id=task_id,
        request_id=request_id,
        route="governed_dialogue",
        answer_text="当前更接近维持高利率观察，而不是马上降息。",
        fallback_used=False,
    )
    failure = dialogue_runtime_service.build_failure(
        task_id=task_id,
        request_id=request_id,
        stage="research",
        cause_category="weak_evidence",
        fallback_behavior="return bounded uncertainty",
    )

    assert conclusion.request_id == request_id
    assert conclusion.evidence_refs == ["https://www.federalreserve.gov/monetarypolicy.htm"]
    assert reply.route == "governed_dialogue"
    assert reply.fallback_used is False
    assert failure.stage == "research"
    assert failure.cause_category == "weak_evidence"
