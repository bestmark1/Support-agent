from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    log_level: str = "INFO"

    supabase_url: str = ""
    supabase_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fitmentor"
    kb_api_base_url: str = "http://127.0.0.1:8000"

    ai_gateway_base_url: str = ""
    ai_gateway_api_key: str = ""
    ai_gateway_model: str = "claude-sonnet-4-6"
    ai_gateway_timeout_seconds: float = 45.0

    telegram_support_bot_token: str = ""
    telegram_support_bot_username: str = ""

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_api_key: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
