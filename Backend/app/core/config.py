try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

from typing import Optional
    

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/eshop"
    SECRET_KEY: str = "replace-me-with-a-secure-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    # Legacy (kept for backward compat)
    OPENAI_API_KEY: Optional[str] = None

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"
    OPENROUTER_MAX_TOKENS: int = 1024
    SITE_URL: str = "https://your-store.com"
    SITE_NAME: str = "Your Electronics Store"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
