from sqlalchemy.orm import Session

from .. import models, repositories


def get_wishlist(db: Session, user_id: str):
    return repositories.get_wishlist(db, user_id)


def add_to_wishlist(db: Session, user_id: str, product_id: str):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.add_to_wishlist(db, user_id, product_id)


def remove_from_wishlist(db: Session, user_id: str, product_id: str):
    removed = repositories.remove_from_wishlist(db, user_id, product_id)
    if not removed:
        raise ValueError("Wishlist item not found")


def get_wishlist_product_ids(db: Session, user_id: str) -> list[str]:
    return repositories.get_wishlist_product_ids(db, user_id)
