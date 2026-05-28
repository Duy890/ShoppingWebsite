"""User routes: profile update."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, repositories, schemas
from ..core.database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["users"])


@router.put("/users/me", response_model=schemas.UserResponse)
def update_profile(payload: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = repositories.update_user_profile(db, current_user, payload.full_name, payload.avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return user
