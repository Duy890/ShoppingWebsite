from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from . import models, repositories
from .core.security import verify_password, hash_password, create_access_token as _create_access_token


def register_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> models.User:
    if repositories.get_user_by_email(db, email):
        raise ValueError("Email already registered")

    hashed_password = hash_password(password)
    return repositories.create_user(db, email=email, hashed_password=hashed_password, full_name=full_name)


def authenticate_user(db: Session, email: str, password: str) -> models.User:
    user = repositories.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")
    return user


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_access_token(subject, expires_delta)


def get_user(db: Session, user_id: str) -> models.User:
    user = repositories.get_user(db, user_id)
    if not user:
        raise ValueError("User not found")
    return user


def update_profile(db: Session, user: models.User, full_name: Optional[str] = None) -> models.User:
    return repositories.update_user_profile(db, user, full_name)


def get_categories(db: Session):
    return repositories.get_categories(db)


def create_category(db: Session, name: str, description: Optional[str] = None):
    return repositories.create_category(db, name, description)


def get_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    return category


def delete_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    if category.products:
        raise ValueError("Category has products and cannot be deleted")
    repositories.delete_category(db, category)


def get_products(db: Session, category_id: Optional[str] = None, search: Optional[str] = None, featured: Optional[bool] = None, sort_by: Optional[str] = None):
    return repositories.get_products(db, category_id, search, featured, sort_by)


def get_product(db: Session, product_id: str):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return product


def create_product(db: Session, product_data: dict):
    return repositories.create_product(db, product_data)


def update_product(db: Session, product_id: str, updates: dict):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.update_product(db, product, updates)


def delete_product(db: Session, product_id: str):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    repositories.delete_product(db, product)


def get_product_reviews(db: Session, product_id: str):
    return repositories.get_reviews_by_product(db, product_id)


def create_review(db: Session, user_id: str, product_id: str, rating: int, comment: Optional[str] = None):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.create_review(db, user_id, product_id, rating, comment)


def get_or_create_cart(db: Session, user_id: str):
    return repositories.get_or_create_cart(db, user_id)


def get_cart_items(db: Session, user_id: str):
    return repositories.get_cart_items(db, user_id)


def add_to_cart(db: Session, user_id: str, product_id: str, quantity: int):
    cart = repositories.get_or_create_cart(db, user_id)
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.add_cart_item(db, cart.id, product_id, quantity)


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


def create_order(db: Session, user_id: str, items: list[dict], shipping_address: Optional[str] = None, payment_method: Optional[str] = None):
    if not items:
        raise ValueError("Order must contain at least one item")

    total_amount = 0.0
    order_items = []

    for item in items:
        product = repositories.get_product(db, item["product_id"])
        if not product:
            raise ValueError(f"Product not found: {item['product_id']}")
        if product.stock < item["quantity"]:
            raise ValueError(f"Insufficient stock for {product.name}")

        product.stock -= item["quantity"]
        total_amount += product.price * item["quantity"]
        order_items.append({
            "product_id": product.id,
            "quantity": item["quantity"],
            "price": product.price,
        })

    order = repositories.create_order(db, user_id, total_amount, shipping_address, payment_method)

    for order_item in order_items:
        repositories.create_order_item(db, order.id, **order_item)

    db.commit()
    return repositories.get_order_by_id(db, order.id)


def get_user_orders(db: Session, user_id: str):
    return repositories.get_orders_by_user(db, user_id)


def get_order(db: Session, order_id: str):
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")
    return order


def get_all_orders(db: Session):
    return repositories.get_all_orders(db)


def update_order_status(db: Session, order_id: str, status: str):
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")
    return repositories.update_order_status(db, order, status)


def get_admin_stats(db: Session):
    return {
        "total_products": repositories.get_product_count(db),
        "total_orders": repositories.get_order_count(db),
        "total_revenue": repositories.get_total_revenue(db),
        "total_users": repositories.get_user_count(db),
    }
