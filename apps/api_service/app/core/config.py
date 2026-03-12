from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "api-service"
    database_url: str = Field(default="postgresql+psycopg://tradechain:tradechain@postgres:5432/tradechain")

    api_service_api_key: str = Field(default="external-dev-key")
    internal_service_api_key: str = Field(default="internal-dev-key")

    ingestion_service_url: str = Field(default="http://ingestion-service:8001")
    agent_core_service_url: str = Field(default="http://agent-core:8002")
    archive_service_url: str = Field(default="http://archive-service:8003")
    evaluation_service_url: str = Field(default="http://evaluation-service:8004")
    internal_http_timeout_seconds: float = Field(default=90.0)
    llm_provider: str = Field(default="heuristic")
    llm_base_url: str = Field(default="https://api.minimaxi.com/v1")
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="MiniMax-M2.5")
    llm_timeout_seconds: float = Field(default=60.0)
    llm_proxy_url: str = Field(default="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
