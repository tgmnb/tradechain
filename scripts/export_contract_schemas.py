import json
from pathlib import Path

from libs.contracts.archive import ArchiveCreate, ArchiveRef
from libs.contracts.event import EventIn, EventNormalized
from libs.contracts.graph import GraphRunRequest, GraphRunResponse
from libs.contracts.proposal import ProposalDraft, ProposalDraftRequest, ProposalFinal
from libs.contracts.review import ReviewRecord
from libs.contracts.task import TaskCreate, TaskRead

MODELS = {
    "TaskCreate": TaskCreate,
    "TaskRead": TaskRead,
    "EventIn": EventIn,
    "EventNormalized": EventNormalized,
    "ProposalDraftRequest": ProposalDraftRequest,
    "ProposalDraft": ProposalDraft,
    "ProposalFinal": ProposalFinal,
    "ReviewRecord": ReviewRecord,
    "ArchiveCreate": ArchiveCreate,
    "ArchiveRef": ArchiveRef,
    "GraphRunRequest": GraphRunRequest,
    "GraphRunResponse": GraphRunResponse,
}


def main() -> None:
    out_dir = Path("libs/contracts/schemas")
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, model in MODELS.items():
        schema_path = out_dir / f"{name}.schema.json"
        schema_path.write_text(
            json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
