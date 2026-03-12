from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="postgresql+psycopg://tradechain:tradechain@postgres:5432/tradechain")
    internal_service_api_key: str = Field(default="internal-dev-key")

    minio_endpoint: str = Field(default="minio:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket: str = Field(default="tradechain-archives")
    minio_secure: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
