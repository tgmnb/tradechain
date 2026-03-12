from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    internal_service_api_key: str = Field(default="internal-dev-key")
    archive_service_url: str = Field(default="http://archive-service:8003")
    llm_provider: str = Field(default="heuristic")
    llm_base_url: str = Field(default="https://api.minimaxi.com/v1")
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="MiniMax-M2.5")
    llm_timeout_seconds: float = Field(default=60.0)
    llm_proxy_url: str = Field(default="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
