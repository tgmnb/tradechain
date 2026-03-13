PROPOSAL_PROFILE_DEFAULTS = {
    "intel_update": {"department_id": "national_statistics_bureau", "specialist_id": "intel_officer"},
    "major_task": {"department_id": "state_council", "specialist_id": "proposal_officer"},
}

PLANNING_PROFILE_DEFAULTS = {
    "daily_preopen": {"department_id": "central_military_commission", "specialist_id": "plan_officer"},
    "major_task": {"department_id": "central_military_commission", "specialist_id": "plan_officer"},
}



def proposal_profile_for(chain_type: str, *, department_id: str | None = None, specialist_id: str | None = None) -> dict[str, str]:
    defaults = PROPOSAL_PROFILE_DEFAULTS.get(chain_type, PROPOSAL_PROFILE_DEFAULTS["major_task"])
    return {
        "department_id": department_id or defaults["department_id"],
        "specialist_id": specialist_id or defaults["specialist_id"],
    }



def planning_profile_for(chain_type: str, *, department_id: str | None = None, specialist_id: str | None = None) -> dict[str, str]:
    defaults = PLANNING_PROFILE_DEFAULTS.get(chain_type, PLANNING_PROFILE_DEFAULTS["daily_preopen"])
    return {
        "department_id": department_id or defaults["department_id"],
        "specialist_id": specialist_id or defaults["specialist_id"],
    }
