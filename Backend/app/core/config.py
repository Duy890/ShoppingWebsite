try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/shopdb"
    SECRET_KEY: str = "replace-me-with-a-secure-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    OPENAI_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
