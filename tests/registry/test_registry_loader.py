from pathlib import Path

import pytest
from pydantic import ValidationError

from libs.contracts.registry import SoulManifest
from libs.registry import load_registry


ROOT = Path(__file__).resolve().parents[2]



def test_load_registry_reads_seed_souls_and_skills() -> None:
    registry = load_registry(ROOT)
    assert "state_council" in registry.departments
    assert "intel_officer" in registry.specialists
    assert "plan_generation_skill" in registry.skills



def test_resolve_agent_profile_merges_department_and_specialist_layers() -> None:
    registry = load_registry(ROOT)
    profile = registry.resolve_agent_profile(chain_type="daily_preopen")

    assert profile.department_id == "central_military_commission"
    assert profile.specialist_id == "plan_officer"
    assert "strategy_synthesis_skill" in profile.skill_names
    assert "plan_generation_skill" in profile.skill_names
    assert any("风险" in item for item in profile.guardrails)



def test_specialist_soul_requires_department_id() -> None:
    with pytest.raises(ValidationError):
        SoulManifest.model_validate(
            {
                "soul_id": "broken_specialist",
                "soul_type": "specialist",
                "version": "v0.1.0",
                "name": "Broken",
                "mission": "missing department",
            }
        )
