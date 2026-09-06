from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # Retrieval configuration
    NEXUS_RERANKER: str = "cross_encoder"

    # Local LLM configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen3:1.7b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()