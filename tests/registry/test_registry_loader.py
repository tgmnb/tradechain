from pathlib import Path

import pytest
from pydantic import ValidationError

from libs.contracts.registry import SoulManifest
from libs.registry import load_registry


ROOT = Path(__file__).resolve().parents[2]



def test_load_registry_reads_seed_souls_and_skills() -> None:
    registry = load_registry(ROOT)
    assert "politburo" in registry.departments
    assert "national_peoples_congress" in registry.departments
    assert "secretariat" in registry.departments
    assert "chairman_officer" in registry.specialists
    assert "review_clerk" in registry.specialists
    assert "record_officer" in registry.specialists
    assert "state_council" in registry.departments
    assert "intel_officer" in registry.specialists
    assert "watch_officer" in registry.specialists
    assert "review_officer" in registry.specialists
    assert "improvement_officer" in registry.specialists
    assert "plan_generation_skill" in registry.skills
    assert "market_scan_skill" in registry.skills
    assert "commodity_logic_skill" in registry.skills
    assert "execution_compare_skill" in registry.skills
    assert "improvement_ticket_skill" in registry.skills
    assert "politburo_direct_reply_skill" in registry.skills
    assert "review_gate_skill" in registry.skills
    assert "archive_registry_skill" in registry.skills
    assert "browser_research_skill" in registry.skills
    assert "government_policy_crawl_skill" in registry.skills



def test_resolve_agent_profile_merges_department_and_specialist_layers() -> None:
    registry = load_registry(ROOT)
    profile = registry.resolve_agent_profile(chain_type="daily_preopen")

    assert profile.department_id == "central_military_commission"
    assert profile.specialist_id == "plan_officer"
    assert "strategy_synthesis_skill" in profile.skill_names
    assert "plan_generation_skill" in profile.skill_names
    assert any("风险" in item for item in profile.guardrails)
    assert any("监控" in item for item in profile.focus)
    assert "中央军委" in profile.system_prompt
    assert "作战" in profile.tone



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


def test_skill_prompts_and_souls_include_richer_runtime_guidance() -> None:
    registry = load_registry(ROOT)
    profile = registry.resolve_agent_profile(chain_type="intel_update")

    news_parse = registry.get_skill("news_parse_skill")
    proposal_draft = registry.get_skill("proposal_draft_skill")
    browser_research = registry.get_skill("browser_research_skill")
    policy_crawl = registry.get_skill("government_policy_crawl_skill")

    assert profile.department_name == "国家统计局"
    assert "news_parse_skill" in profile.skill_names
    assert "proposal_draft_skill" in profile.skill_names
    assert "browser_research_skill" in profile.skill_names
    assert "government_policy_crawl_skill" in profile.skill_names
    assert any("来源" in item for item in profile.guardrails)
    assert "待验证" in news_parse.prompt_template
    assert "research_questions" in proposal_draft.prompt_template
    assert browser_research.skill_type == "functional"
    assert browser_research.runtime["adapter"] == "agent_browser"
    assert policy_crawl.skill_type == "functional"
    assert policy_crawl.runtime["runtime_kind"] == "local_python"


def test_future_chain_profiles_resolve_to_seeded_specialists() -> None:
    registry = load_registry(ROOT)

    direct_dialogue = registry.resolve_agent_profile(chain_type="direct_dialogue", department_id="politburo")
    intraday = registry.resolve_agent_profile(chain_type="intraday_watch")
    postclose = registry.resolve_agent_profile(chain_type="postclose_review")
    nightly = registry.resolve_agent_profile(chain_type="nightly_improvement")

    assert direct_dialogue.specialist_id == "chairman_officer"
    assert "politburo_direct_reply_skill" in direct_dialogue.skill_names

    assert intraday.specialist_id == "watch_officer"
    assert "market_scan_skill" in intraday.skill_names
    assert "strategy_synthesis_skill" in intraday.skill_names
    assert "plan_generation_skill" in intraday.skill_names

    assert postclose.specialist_id == "review_officer"
    assert "execution_compare_skill" in postclose.skill_names
    assert "strategy_synthesis_skill" in postclose.skill_names

    assert nightly.department_id == "state_council"
    assert nightly.specialist_id == "improvement_officer"
    assert "improvement_ticket_skill" in nightly.skill_names
    assert "proposal_draft_skill" in nightly.skill_names
