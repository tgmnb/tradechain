import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.contracts.archive import ArchiveCreate, ArchiveRef
from libs.contracts.event import EventIn, EventNormalized
from libs.contracts.graph import GraphRunRequest, GraphRunResponse
from libs.contracts.proposal import ProposalDraft, ProposalDraftRequest, ProposalFinal
from libs.contracts.registry import ResolvedAgentProfile, SkillManifest, SoulManifest
from libs.contracts.research import ResearchReport, ResearchReportDraftRequest
from libs.contracts.review import PostcloseReview, ReviewRecord
from libs.contracts.strategy import Strategy, StrategyDraftRequest
from libs.contracts.task import TaskCreate, TaskRead
from libs.contracts.trading import ExecutionRecord, ExecutionRecordCreateRequest, TradingPlan, TradingPlanDraftRequest

MODELS = {
    "TaskCreate": TaskCreate,
    "TaskRead": TaskRead,
    "EventIn": EventIn,
    "EventNormalized": EventNormalized,
    "ProposalDraftRequest": ProposalDraftRequest,
    "ProposalDraft": ProposalDraft,
    "ProposalFinal": ProposalFinal,
    "PostcloseReview": PostcloseReview,
    "ReviewRecord": ReviewRecord,
    "ArchiveCreate": ArchiveCreate,
    "ArchiveRef": ArchiveRef,
    "GraphRunRequest": GraphRunRequest,
    "GraphRunResponse": GraphRunResponse,
    "SoulManifest": SoulManifest,
    "SkillManifest": SkillManifest,
    "ResolvedAgentProfile": ResolvedAgentProfile,
    "ResearchReportDraftRequest": ResearchReportDraftRequest,
    "ResearchReport": ResearchReport,
    "StrategyDraftRequest": StrategyDraftRequest,
    "Strategy": Strategy,
    "TradingPlanDraftRequest": TradingPlanDraftRequest,
    "TradingPlan": TradingPlan,
    "ExecutionRecordCreateRequest": ExecutionRecordCreateRequest,
    "ExecutionRecord": ExecutionRecord,
}



def main() -> None:
    out_dir = ROOT / "libs" / "contracts" / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, model in MODELS.items():
        schema_path = out_dir / f"{name}.schema.json"
        schema_path.write_text(
            json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
