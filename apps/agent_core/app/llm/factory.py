from __future__ import annotations

from functools import lru_cache

from apps.agent_core.app.config import get_settings
from apps.agent_core.app.llm.base import ProposalGenerator
from apps.agent_core.app.llm.heuristic import HeuristicProposalGenerator
from apps.agent_core.app.llm.minimax import MiniMaxProposalGenerator


@lru_cache
def get_proposal_generator() -> ProposalGenerator:
    settings = get_settings()
    provider = settings.llm_provider.strip().lower()

    if provider == "minimax":
        return MiniMaxProposalGenerator(settings)
    return HeuristicProposalGenerator()
