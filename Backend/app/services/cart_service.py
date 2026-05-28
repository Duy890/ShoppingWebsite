from typing import Optional

from sqlalchemy.orm import Session

from .. import models, repositories


def get_or_create_cart(db: Session, user_id: str):
    return repositories.get_or_create_cart(db, user_id)


def get_cart_items(db: Session, user_id: str):
    return repositories.get_cart_items(db, user_id)


def add_to_cart(db: Session, user_id: str, product_id: str, quantity: int, variant_id: Optional[str] = None):
    cart = repositories.get_or_create_cart(db, user_id)
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")

    if variant_id:
        variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
        if not variant:
            raise ValueError("Variant not found")

    return repositories.add_cart_item(db, cart.id, product_id, quantity, variant_id)


def update_cart_item(db: Session, item_id: str, quantity: int):
    item = repositories.get_cart_item_by_id(db, item_id)
    if not item:
        raise ValueError("Cart item not found")
    return repositories.update_cart_item(db, item, quantity)


def remove_cart_item(db: Session, item_id: str):
    item = repositories.get_cart_item_by_id(db, item_id)
    if not item:
        raise ValueError("Cart item not found")
    repositories.delete_cart_item(db, item)


def clear_cart(db: Session, user_id: str):
    repositories.clear_cart(db, user_id)
