"""Cart routes: CRUD with variant support."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import cart_service
from ..core.database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["cart"])


@router.get("/cart", response_model=schemas.CartRead)
def read_cart(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.get_or_create_cart(db, current_user.id)
    items = cart_service.get_cart_items(db, current_user.id)
    cart.items = items
    return cart


@router.post("/cart/items", response_model=schemas.CartItemRead)
def add_cart_item(payload: schemas.CartItemCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return cart_service.add_to_cart(db, current_user.id, payload.product_id, payload.quantity, payload.variant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/cart/items/{item_id}", response_model=schemas.CartItemRead)
def modify_cart_item(item_id: str, payload: schemas.CartItemUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return cart_service.update_cart_item(db, item_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(item_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        cart_service.remove_cart_item(db, item_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/cart/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service.clear_cart(db, current_user.id)
