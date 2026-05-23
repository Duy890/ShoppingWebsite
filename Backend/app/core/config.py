import os

try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

from typing import Optional


ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/shopdb"
    SECRET_KEY: str = "replace-me-with-a-secure-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    # Legacy (kept for backward compat)
    OPENAI_API_KEY: Optional[str] = None

    # MoMo Payment (Sandbox)
    MOMO_PARTNER_CODE: str = ""
    MOMO_ACCESS_KEY: str = ""
    MOMO_SECRET_KEY: str = ""
    MOMO_ENDPOINT: str = "https://test-payment.momo.vn/v2/gateway/api/create"
    MOMO_REDIRECT_URL: str = "http://localhost:5173/payment/result"
    MOMO_IPN_URL: str = ""
    # Change to a real webhook.site URL or ngrok HTTPS URL for MoMo IPN callbacks

    # Email / SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "duyl2282@gmail.com"           # Your Gmail address, e.g. yourapp@gmail.com
    SMTP_PASSWORD: str = "isor zduw rprf yaqn"       # Gmail App Password (NOT your login password)
    SMTP_FROM_NAME: str = "Electronics Store"
    FRONTEND_URL: str = "http://localhost:5173"

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
