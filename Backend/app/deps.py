"""Shared dependencies for all route modules.

Extracted from controllers.py to avoid circular imports and standardize
auth, admin checks, and upload helpers across all domain routers.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import Depends, HTTPException, Request, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .services import auth_service
from .core.database import get_db
from .core.security import decode_access_token

# ── Auth Dependencies ──────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_optional_user(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> models.User | None:
    try:
        return get_current_user(token, db)
    except Exception:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    try:
        user = auth_service.get_user(db, user_id)
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )


def require_admin(user: models.User) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


# ── Upload Helpers ─────────────────────────────────────────────────

UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def build_image_url(filename: str, request: Request) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/uploads/images/{filename}"


def get_safe_image_extension(file: UploadFile) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed",
        )
    return extension
