from collections.abc import Generator

from sqlalchemy.orm import Session

from apps.archive_service.app.config import get_settings
from libs.db.session import build_engine, build_session_factory

settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = build_session_factory(settings.database_url)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
