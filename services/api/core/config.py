from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://careeros:careeros_dev@localhost:5432/careeros"
    database_url_sync: str = "postgresql://careeros:careeros_dev@localhost:5432/careeros"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o"
    auth_secret: str = ""
    api_url: str = "http://localhost:8000"
    log_level: str = "DEBUG"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
