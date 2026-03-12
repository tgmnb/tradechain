from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    internal_service_api_key: str = Field(default="internal-dev-key")
    archive_service_url: str = Field(default="http://archive-service:8003")


@lru_cache
def get_settings() -> Settings:
    return Settings()
