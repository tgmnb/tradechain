from typing import Literal

from pydantic import Field, model_validator

from libs.contracts.base import ContractModel


_SLUG_PATTERN = r"^[a-z0-9_]+$"


class SkillManifest(ContractModel):
    skill_name: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(default="v0.1.0", min_length=1, max_length=50)
    owner_department: str | None = Field(default=None, max_length=100)
    status: str = Field(default="draft", max_length=30)
    description: str = Field(min_length=1, max_length=500)
    input_schema: str = Field(min_length=1, max_length=100)
    output_schema: str = Field(min_length=1, max_length=100)
    chain_types: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    prompt_template: str = Field(min_length=1)


class SoulManifest(ContractModel):
    soul_id: str = Field(pattern=_SLUG_PATTERN)
    soul_type: Literal["department", "specialist"]
    version: str = Field(default="v0.1.0", min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    department_id: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    department_name: str | None = Field(default=None, max_length=100)
    mission: str = Field(min_length=1)
    responsibilities: list[str] = Field(default_factory=list)
    focus: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    style_notes: list[str] = Field(default_factory=list)
    tone: str = Field(default="", max_length=200)
    default_specialist: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    default_skills: list[str] = Field(default_factory=list)
    additional_skills: list[str] = Field(default_factory=list)
    chain_bindings: dict[str, dict[str, str]] = Field(default_factory=dict)
    status: str = Field(default="draft", max_length=30)

    @model_validator(mode="after")
    def validate_shape(self) -> "SoulManifest":
        if self.soul_type == "department":
            if not self.department_name:
                raise ValueError("department souls must define department_name")
            if self.department_id and self.department_id != self.soul_id:
                raise ValueError("department soul department_id must match soul_id when provided")
            self.department_id = self.soul_id
        else:
            if not self.department_id:
                raise ValueError("specialist souls must define department_id")
            if self.default_specialist:
                raise ValueError("specialist souls cannot define default_specialist")
            if self.default_skills:
                raise ValueError("specialist souls cannot define default_skills")
        return self


class ResolvedSkillBinding(ContractModel):
    skill_name: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=500)
    input_schema: str = Field(min_length=1, max_length=100)
    output_schema: str = Field(min_length=1, max_length=100)
    prompt_template: str = Field(min_length=1)
    owner_department: str | None = Field(default=None, max_length=100)


class ResolvedAgentProfile(ContractModel):
    department_id: str = Field(pattern=_SLUG_PATTERN)
    department_name: str = Field(min_length=1, max_length=100)
    department_soul_id: str = Field(pattern=_SLUG_PATTERN)
    specialist_id: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    specialist_name: str | None = Field(default=None, max_length=100)
    chain_type: str = Field(min_length=1, max_length=50)
    mission: str = Field(min_length=1)
    responsibilities: list[str] = Field(default_factory=list)
    focus: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    style_notes: list[str] = Field(default_factory=list)
    tone: str = Field(default="", max_length=200)
    skill_names: list[str] = Field(default_factory=list)
    skills: list[ResolvedSkillBinding] = Field(default_factory=list)
    system_prompt: str = Field(min_length=1)
