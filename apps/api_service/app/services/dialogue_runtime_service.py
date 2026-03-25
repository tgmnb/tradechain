from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import httpx
from fastapi import Request
from sqlalchemy.orm import Session

from apps.api_service.app.core.config import get_settings
from libs.contracts.archive import ArchiveCreate, ArchiveRef
from libs.contracts.dialogue import ConclusionDraft, DialogueFailureState, DialogueIntent, DialogueReply, EvidenceBundle
from libs.db.models import TaskModel


class DialogueRuntimeService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_dialogue_task(
        self,
        db: Session,
        *,
        payload: dict[str, Any],
        route: str,
        objective: str,
        requested_output: str = "briefing",
        requires_research: bool,
    ) -> tuple[TaskModel, DialogueIntent]:
        conversation_id = str(payload.get("conversation_id") or uuid4())
        request_id = str(payload.get("request_id") or uuid4())
        created_at = datetime.now(timezone.utc)
        task = TaskModel(
            id=uuid4(),
            title=_title_from_text(str(payload.get("text") or "")),
            type="dialogue_request",
            source="discord",
            chain_type="direct_dialogue",
            priority=50,
            created_by=str(payload.get("user_name") or "user"),
            goal_json={"text": payload.get("text", "")},
            context_json={
                "conversation_id": conversation_id,
                "request_id": request_id,
                "route": route,
                "requested_output": requested_output,
            },
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        intent = DialogueIntent(
            id=uuid4(),
            task_id=task.id,
            request_id=request_id,
            conversation_id=conversation_id,
            user_text=str(payload.get("text") or "").strip(),
            route=route,
            objective=objective,
            topic_scope=list(payload.get("topic_scope") or []),
            constraints=list(payload.get("constraints") or []),
            requested_output=requested_output,
            requires_research=requires_research,
            metadata={
                "entry_layer": "politburo",
                "user_name": payload.get("user_name"),
                "channel_id": payload.get("channel_id"),
                "guild_id": payload.get("guild_id"),
            },
            created_at=created_at,
        )
        return task, intent

    def build_reply(
        self,
        *,
        task_id: UUID,
        request_id: str,
        route: str,
        answer_text: str,
        archive_refs: list[dict[str, Any]] | None = None,
        fallback_used: bool = False,
        failure_stage: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DialogueReply:
        return DialogueReply(
            id=uuid4(),
            task_id=task_id,
            request_id=request_id,
            route=route,
            answer_text=answer_text,
            fallback_used=fallback_used,
            failure_stage=failure_stage,
            archive_refs=archive_refs or [],
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )

    def build_conclusion(
        self,
        *,
        task_id: UUID,
        request_id: str,
        summary: str,
        key_points: list[str] | None = None,
        risks: list[str] | None = None,
        recommended_action: str = "notify",
        confidence: float = 0.5,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConclusionDraft:
        return ConclusionDraft(
            id=uuid4(),
            task_id=task_id,
            request_id=request_id,
            summary=summary,
            key_points=key_points or [],
            risks=risks or [],
            recommended_action=recommended_action,
            confidence=confidence,
            evidence_refs=evidence_refs or [],
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )

    def build_failure(
        self,
        *,
        task_id: UUID,
        request_id: str,
        stage: str,
        cause_category: str,
        fallback_behavior: str,
        retryable: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> DialogueFailureState:
        return DialogueFailureState(
            id=uuid4(),
            task_id=task_id,
            request_id=request_id,
            stage=stage,
            cause_category=cause_category,
            fallback_behavior=fallback_behavior,
            retryable=retryable,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )

    def archive_dialogue_artifacts(
        self,
        request: Request,
        *,
        intent: DialogueIntent | None = None,
        evidence_bundle: EvidenceBundle | None = None,
        conclusion: ConclusionDraft | None = None,
        reply: DialogueReply | None = None,
        failure: DialogueFailureState | None = None,
    ) -> list[dict[str, Any]]:
        archive_refs: list[dict[str, Any]] = []
        for object_type, artifact in (
            ("dialogue_intent", intent),
            ("evidence_bundle", evidence_bundle),
            ("dialogue_conclusion", conclusion),
            ("dialogue_reply", reply),
            ("dialogue_failure", failure),
        ):
            if artifact is None:
                continue
            archive_ref = self._archive_one(request, object_type=object_type, payload=artifact.model_dump(mode="json"))
            if archive_ref:
                archive_refs.append(archive_ref.model_dump(mode="json"))
        return archive_refs

    def _archive_one(self, request: Request, *, object_type: str, payload: dict[str, Any]) -> ArchiveRef | None:
        object_id = UUID(str(payload["id"]))
        archive_payload = ArchiveCreate(
            object_type=object_type,
            object_id=object_id,
            payload=payload,
            metadata={
                "request_id": payload.get("request_id"),
                "task_id": payload.get("task_id"),
                "chain_type": "direct_dialogue",
                "version": payload.get("schema_version"),
            },
        )
        headers = {
            "X-API-Key": self.settings.internal_service_api_key,
            "X-Request-ID": request.headers.get("X-Request-ID", str(uuid4())),
            "X-Chain-Type": "direct_dialogue",
            "X-Actor": request.headers.get("X-Actor", "api-service"),
        }
        try:
            with httpx.Client(timeout=10.0, trust_env=False) as client:
                response = client.post(
                    f"{self.settings.archive_service_url}/internal/archive",
                    json=archive_payload.model_dump(mode="json"),
                    headers=headers,
                )
            response.raise_for_status()
        except Exception:
            return None
        return ArchiveRef.model_validate(response.json())


dialogue_runtime_service = DialogueRuntimeService()


def _title_from_text(text: str) -> str:
    compact = " ".join(text.split())
    return compact[:200] if compact else "Dialogue request"
