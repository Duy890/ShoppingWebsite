"""Upload routes: image and avatar uploads."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from .. import models
from ..core.database import get_db
from ..deps import (
    UPLOAD_DIR,
    MAX_IMAGE_SIZE,
    build_image_url,
    get_safe_image_extension,
    get_current_user,
    require_admin,
)

router = APIRouter(tags=["uploads"])


@router.post("/upload-image")
def upload_image(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    extension = get_safe_image_extension(file)
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save uploaded image") from exc

    return {"image_url": build_image_url(filename, request)}


@router.post("/upload-avatar")
def upload_avatar(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    extension = get_safe_image_extension(file)
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save uploaded avatar") from exc

    return {"avatar_url": build_image_url(filename, request)}
