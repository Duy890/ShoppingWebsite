"""Wishlist routes: CRUD with product ID list support."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import wishlist_service
from ..core.database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["wishlist"])


@router.get("/wishlist", response_model=schemas.WishlistRead)
def read_wishlist(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = wishlist_service.get_wishlist(db, current_user.id)
    return {"items": items}


@router.get("/wishlist/ids", response_model=list[str])
def read_wishlist_ids(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return wishlist_service.get_wishlist_product_ids(db, current_user.id)


@router.post("/wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
def add_wishlist(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return wishlist_service.add_to_wishlist(db, current_user.id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_wishlist(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        wishlist_service.remove_from_wishlist(db, current_user.id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
