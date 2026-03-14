from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from libs.contracts.registry import (
    ResolvedAgentProfile,
    ResolvedSkillBinding,
    SkillManifest,
    SoulManifest,
)


class RegistryError(RuntimeError):
    pass


@dataclass(slots=True)
class RegistryBundle:
    departments: dict[str, SoulManifest]
    specialists: dict[str, SoulManifest]
    skills: dict[str, SkillManifest]
    department_skill_map: dict[str, list[str]]
    specialist_skill_map: dict[str, list[str]]

    def list_souls(self) -> list[SoulManifest]:
        return sorted([*self.departments.values(), *self.specialists.values()], key=lambda item: item.soul_id)

    def list_skills(self) -> list[SkillManifest]:
        return sorted(self.skills.values(), key=lambda item: item.skill_name)

    def get_soul(self, soul_id: str) -> SoulManifest:
        soul = self.departments.get(soul_id) or self.specialists.get(soul_id)
        if not soul:
            raise RegistryError(f"soul not found: {soul_id}")
        return soul

    def get_skill(self, skill_name: str) -> SkillManifest:
        skill = self.skills.get(skill_name)
        if not skill:
            raise RegistryError(f"skill not found: {skill_name}")
        return skill

    def resolve_agent_profile(
        self,
        *,
        chain_type: str,
        department_id: str | None = None,
        specialist_id: str | None = None,
    ) -> ResolvedAgentProfile:
        department = self._select_department(chain_type=chain_type, department_id=department_id, specialist_id=specialist_id)
        specialist = self._select_specialist(chain_type=chain_type, department=department, specialist_id=specialist_id)

        skill_names: list[str] = []
        specialist_skill_names = self.specialist_skill_map.get(specialist.soul_id, []) if specialist else []
        for name in [
            *self.department_skill_map.get(department.soul_id, []),
            *department.default_skills,
            *specialist_skill_names,
            *(specialist.additional_skills if specialist else []),
        ]:
            if name not in skill_names:
                skill_names.append(name)

        skills = [
            ResolvedSkillBinding(
                skill_name=skill.skill_name,
                version=skill.version,
                skill_type=skill.skill_type,
                description=skill.description,
                input_schema=skill.input_schema,
                output_schema=skill.output_schema,
                prompt_template=skill.prompt_template,
                owner_department=skill.owner_department,
                runtime=skill.runtime,
            )
            for skill in (self.get_skill(name) for name in skill_names)
        ]

        responsibilities = [*department.responsibilities, *(specialist.responsibilities if specialist else [])]
        focus = list(specialist.focus if specialist else [])
        guardrails = [*department.guardrails, *(specialist.guardrails if specialist else [])]
        style_notes = [*department.style_notes, *(specialist.style_notes if specialist else [])]
        tone = specialist.tone if specialist and specialist.tone else department.tone

        system_prompt = _build_system_prompt(
            department=department,
            specialist=specialist,
            chain_type=chain_type,
            responsibilities=responsibilities,
            focus=focus,
            guardrails=guardrails,
            style_notes=style_notes,
            skills=skills,
            tone=tone,
        )

        return ResolvedAgentProfile(
            department_id=department.department_id or department.soul_id,
            department_name=department.department_name or department.name,
            department_soul_id=department.soul_id,
            specialist_id=specialist.soul_id if specialist else None,
            specialist_name=specialist.name if specialist else None,
            chain_type=chain_type,
            mission=specialist.mission if specialist else department.mission,
            responsibilities=responsibilities,
            focus=focus,
            guardrails=guardrails,
            style_notes=style_notes,
            tone=tone,
            skill_names=skill_names,
            skills=skills,
            system_prompt=system_prompt,
        )

    def _select_department(
        self,
        *,
        chain_type: str,
        department_id: str | None,
        specialist_id: str | None,
    ) -> SoulManifest:
        if department_id:
            department = self.get_soul(department_id)
            if department.soul_type != "department":
                raise RegistryError(f"department id does not reference a department soul: {department_id}")
            return department

        if specialist_id:
            specialist = self.get_soul(specialist_id)
            if specialist.soul_type != "specialist":
                raise RegistryError(f"specialist id does not reference a specialist soul: {specialist_id}")
            return self.get_soul(specialist.department_id or "")

        preferred = [soul for soul in self.departments.values() if chain_type in soul.chain_bindings]
        fallback = [soul for soul in self.departments.values() if soul.default_specialist]
        candidates = preferred or fallback
        if not candidates:
            raise RegistryError(f"no department soul available for chain_type={chain_type}")
        return sorted(candidates, key=lambda item: item.soul_id)[0]

    def _select_specialist(
        self,
        *,
        chain_type: str,
        department: SoulManifest,
        specialist_id: str | None,
    ) -> SoulManifest | None:
        if specialist_id:
            specialist = self.get_soul(specialist_id)
            if specialist.soul_type != "specialist":
                raise RegistryError(f"specialist id does not reference a specialist soul: {specialist_id}")
            if specialist.department_id != department.soul_id:
                raise RegistryError("specialist soul department mismatch")
            return specialist

        chain_binding = department.chain_bindings.get(chain_type, {})
        configured = chain_binding.get("specialist") or department.default_specialist
        if configured:
            specialist = self.get_soul(configured)
            if specialist.soul_type != "specialist":
                raise RegistryError(f"default specialist must reference specialist soul: {configured}")
            return specialist

        matches = [
            soul
            for soul in self.specialists.values()
            if soul.department_id == department.soul_id and (not soul.chain_bindings or chain_type in soul.chain_bindings)
        ]
        return sorted(matches, key=lambda item: item.soul_id)[0] if matches else None


def load_registry(root: str | Path | None = None) -> RegistryBundle:
    base = Path(root or ".").resolve()
    department_dir = base / "configs" / "departments"

    departments: dict[str, SoulManifest] = {}
    specialists: dict[str, SoulManifest] = {}
    skills: dict[str, SkillManifest] = {}
    department_skill_map: dict[str, list[str]] = {}
    specialist_skill_map: dict[str, list[str]] = {}

    for dept_path in sorted(path for path in department_dir.iterdir() if path.is_dir()):
        soul_path = dept_path / "soul.yaml"
        if not soul_path.exists():
            raise RegistryError(f"department soul missing: {soul_path}")

        department = SoulManifest.model_validate({**_read_yaml(soul_path), "soul_type": "department"})
        if department.soul_id in departments:
            raise RegistryError(f"duplicate department soul id: {department.soul_id}")
        departments[department.soul_id] = department
        department_skill_map[department.soul_id] = _load_skills_from_dir(dept_path / "skills", skills)

        specialist_root = dept_path / "specialists"
        if not specialist_root.exists():
            continue

        for specialist_path in sorted(path for path in specialist_root.iterdir() if path.is_dir()):
            specialist_soul_path = specialist_path / "soul.yaml"
            if not specialist_soul_path.exists():
                raise RegistryError(f"specialist soul missing: {specialist_soul_path}")

            specialist = SoulManifest.model_validate({**_read_yaml(specialist_soul_path), "soul_type": "specialist"})
            if specialist.department_id != department.soul_id:
                raise RegistryError(
                    f"specialist soul department mismatch: {specialist.soul_id} expected {department.soul_id}, "
                    f"got {specialist.department_id}"
                )
            if specialist.soul_id in specialists:
                raise RegistryError(f"duplicate specialist soul id: {specialist.soul_id}")
            specialists[specialist.soul_id] = specialist
            specialist_skill_map[specialist.soul_id] = _load_skills_from_dir(specialist_path / "skills", skills)

    return RegistryBundle(
        departments=departments,
        specialists=specialists,
        skills=skills,
        department_skill_map=department_skill_map,
        specialist_skill_map=specialist_skill_map,
    )


def _load_skills_from_dir(directory: Path, skills: dict[str, SkillManifest]) -> list[str]:
    if not directory.exists():
        return []

    discovered: list[str] = []
    for manifest_path in sorted(directory.glob("*/manifest.yaml")):
        skill = _load_skill_manifest(manifest_path)
        if skill.skill_name in skills:
            raise RegistryError(f"duplicate skill name: {skill.skill_name}")
        skills[skill.skill_name] = skill
        discovered.append(skill.skill_name)
    return discovered


def _load_skill_manifest(manifest_path: Path) -> SkillManifest:
    payload = _read_yaml(manifest_path)
    prompt_file = payload.pop("prompt_file", "prompt.md")
    prompt_path = manifest_path.with_name(prompt_file)
    if not prompt_path.exists():
        raise RegistryError(f"skill prompt missing: {prompt_path}")
    return SkillManifest.model_validate(
        {
            **payload,
            "prompt_template": prompt_path.read_text(encoding="utf-8").strip(),
        }
    )


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise RegistryError(f"manifest must be a mapping: {path}")
    return payload


def _build_system_prompt(
    *,
    department: SoulManifest,
    specialist: SoulManifest | None,
    chain_type: str,
    responsibilities: list[str],
    focus: list[str],
    guardrails: list[str],
    style_notes: list[str],
    skills: list[ResolvedSkillBinding],
    tone: str,
) -> str:
    parts = [
        f"Chain Type: {chain_type}",
        f"Department: {department.department_name or department.name}",
        f"Department Mission: {department.mission}",
    ]
    if specialist:
        parts.append(f"Specialist: {specialist.name}")
        parts.append(f"Specialist Mission: {specialist.mission}")
    if responsibilities:
        parts.append("Responsibilities:\n- " + "\n- ".join(responsibilities))
    if focus:
        parts.append("Focus:\n- " + "\n- ".join(focus))
    if guardrails:
        parts.append("Guardrails:\n- " + "\n- ".join(guardrails))
    if style_notes:
        parts.append("Style Notes:\n- " + "\n- ".join(style_notes))
    if tone:
        parts.append(f"Tone: {tone}")
    if skills:
        parts.append(
            "Active Skills:\n- "
            + "\n- ".join(f"{skill.skill_name}: {skill.description}" for skill in skills)
        )
    return "\n\n".join(parts)
