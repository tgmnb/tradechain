import os
import sys
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from libs.db.models import SkillVersionModel, SoulVersionModel
from libs.db.session import build_session_factory
from libs.registry import load_registry



def _stable_uuid(*parts: str):
    return uuid5(NAMESPACE_URL, "tradechain:" + ":".join(parts))



def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    registry = load_registry(ROOT)
    session_factory = build_session_factory(database_url)
    session = session_factory()
    try:
        for soul in registry.list_souls():
            row = session.scalar(
                select(SoulVersionModel).where(
                    SoulVersionModel.soul_id == soul.soul_id,
                    SoulVersionModel.version == soul.version,
                )
            )
            if not row:
                row = SoulVersionModel(id=_stable_uuid("soul", soul.soul_id, soul.version))
                session.add(row)
            row.soul_id = soul.soul_id
            row.soul_type = soul.soul_type
            row.name = soul.name
            row.department_id = soul.department_id
            row.version = soul.version
            row.status = soul.status
            row.manifest = soul.model_dump(mode="json")
            row.changelog = "Synced from filesystem registry."

        for skill in registry.list_skills():
            row = session.scalar(
                select(SkillVersionModel).where(
                    SkillVersionModel.skill_name == skill.skill_name,
                    SkillVersionModel.version == skill.version,
                )
            )
            if not row:
                row = SkillVersionModel(id=_stable_uuid("skill", skill.skill_name, skill.version))
                session.add(row)
            row.skill_name = skill.skill_name
            row.version = skill.version
            row.owner_department = skill.owner_department
            row.status = skill.status
            row.manifest = skill.model_dump(mode="json")
            row.test_result = {"synced_from": "filesystem", "cases": 0, "pass_rate": 0}
            row.changelog = "Synced from filesystem registry."

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
