from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Centralized config (12-factor).
    - All runtime settings come from environment variables
    - Keeps secrets out of code
    - Makes local/dev/prod consistent
    """
    app_env: str = Field(default="dev", alias="APP_ENV")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_timeout_s: float = Field(default=20.0, alias="OPENAI_TIMEOUT_S")
    openai_max_retries: int = Field(default=2, alias="OPENAI_MAX_RETRIES")

    default_chat_model: str = Field(default="gpt-4o-mini", alias="DEFAULT_CHAT_MODEL")
    default_embed_model: str = Field(default="text-embedding-3-small", alias="DEFAULT_EMBED_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()