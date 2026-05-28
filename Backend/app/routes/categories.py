"""Category routes: CRUD + tree + search suggestions."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import category_service
from ..core.admin_security import log_admin_action
from ..core.database import get_db
from ..deps import get_current_user, require_admin

router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[schemas.CategoryRead])
def read_categories(db: Session = Depends(get_db)):
    return category_service.get_categories(db)


@router.get("/categories/tree", response_model=list[schemas.CategoryTreeRead])
def read_category_tree(db: Session = Depends(get_db)):
    return category_service.get_categories_tree(db)


@router.post("/categories", response_model=schemas.CategoryRead)
def create_category(payload: schemas.CategoryCreate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = category_service.create_category(db, payload.name, payload.description, payload.parent_id)
        log_admin_action(
            db, current_user.id, "category.create", "category", result.id,
            details={"name": result.name},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "category.create.failed", "category", None,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        category_service.delete_category(db, category_id)
        log_admin_action(
            db, current_user.id, "category.delete", "category", category_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "category.delete.failed", "category", category_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/search/suggestions", response_model=list[schemas.SearchSuggestionRead])
def read_search_suggestions(q: str | None = None, db: Session = Depends(get_db)):
    return category_service.get_search_suggestions(db, q or "")
