import os
import warnings
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# =========================================================
# BASE DIRECTORY
# =========================================================

# Example:
# Backend/
# ├── .env
# ├── app/
# │   ├── core/
# │   │   └── config.py

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"


# =========================================================
# SETTINGS
# =========================================================

class Settings(BaseSettings):

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL: str = Field(...)

    # =====================================================
    # JWT AUTH
    # =====================================================

    SECRET_KEY: str = Field(...)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    ALGORITHM: str = "HS256"

    # =====================================================
    # LEGACY OPENAI SUPPORT
    # =====================================================

    OPENAI_API_KEY: Optional[str] = None

    # =====================================================
    # MOMO PAYMENT
    # =====================================================

    MOMO_PARTNER_CODE: str = ""
    MOMO_ACCESS_KEY: str = ""
    MOMO_SECRET_KEY: str = ""

    MOMO_ENDPOINT: str = (
        "https://test-payment.momo.vn/v2/gateway/api/create"
    )

    MOMO_REDIRECT_URL: str = (
        "http://localhost:5173/payment/result"
    )

    MOMO_IPN_URL: str = ""

    # =====================================================
    # SMTP / EMAIL
    # =====================================================

    SMTP_HOST: str = "smtp.gmail.com"

    SMTP_PORT: int = 587

    SMTP_USER: str = ""

    SMTP_PASSWORD: str = ""

    SMTP_FROM_NAME: str = "Electronics Store"

    # =====================================================
    # FRONTEND
    # =====================================================

    FRONTEND_URL: str = "http://localhost:5173"

    # =====================================================
    # OPENROUTER AI
    # =====================================================

    OPENROUTER_API_KEY: Optional[str] = None

    OPENROUTER_MODEL: str = (
        "google/gemini-2.0-flash-001"
    )

    OPENROUTER_MAX_TOKENS: int = 1024

    SITE_URL: str = "https://your-store.com"

    SITE_NAME: str = "Your Electronics Store"

    # =====================================================
    # CORS
    # =====================================================

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # =====================================================
    # PYDANTIC SETTINGS CONFIG
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# =========================================================
# SETTINGS FACTORY  (mtime-based auto-reload)
# =========================================================

_settings_instance: Settings | None = None
_settings_mtime: float = 0


def get_settings() -> Settings:
    """Return cached Settings, auto-reloading when .env has changed on disk."""
    global _settings_instance, _settings_mtime

    current_mtime = ENV_FILE.stat().st_mtime if ENV_FILE.exists() else 0

    if _settings_instance is None or current_mtime > _settings_mtime:
        _settings_instance = Settings()
        _settings_mtime = current_mtime

        _check_os_env_override("OPENROUTER_API_KEY")
        _check_os_env_override("DATABASE_URL")
        _check_os_env_override("SECRET_KEY")

    return _settings_instance


def _check_os_env_override(name: str) -> None:
    """Warn if an OS environment variable will shadow .env values."""
    env_val = os.environ.get(name)
    file_val = getattr(_settings_instance, name, None)
    if env_val is not None and file_val is not None and env_val != file_val:
        warnings.warn(
            f"OS env ${name} differs from .env value — OS env takes precedence. "
            f"If you meant to use the .env value, run `unset {name}` first."
        )


# =========================================================
# LEGACY SINGLETON  (backward-compatible, prefer get_settings())
# =========================================================

settings = get_settings()


# =========================================================
# DEBUG LOGS
# =========================================================

print("=" * 60)
print("CONFIG LOADED")
print("=" * 60)

print("BASE_DIR:")
print(BASE_DIR)

print("\nENV FILE:")
print(ENV_FILE)

print("\nDATABASE:")
print(settings.DATABASE_URL)

print("\nOPENROUTER MODEL:")
print(settings.OPENROUTER_MODEL)

print("\nOPENROUTER KEY EXISTS:")
print(bool(settings.OPENROUTER_API_KEY))

print("=" * 60)