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


def update_profile(db: Session, user: models.User, full_name: Optional[str] = None, avatar_url: Optional[str] = None) -> models.User:
    return repositories.update_user_profile(db, user, full_name, avatar_url)


def get_user_addresses(db: Session, user_id: str):
    return repositories.get_addresses_by_user(db, user_id)


def create_address(db: Session, user_id: str, address_data: dict):
    return repositories.create_address(db, user_id, address_data)


def update_address(db: Session, user_id: str, address_id: str, updates: dict):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    return repositories.update_address(db, address, updates)


def delete_address(db: Session, user_id: str, address_id: str):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    repositories.delete_address(db, address)


def set_default_address(db: Session, user_id: str, address_id: str):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    return repositories.set_default_address(db, address)


def get_categories(db: Session):
    return repositories.get_categories(db)


def get_categories_tree(db: Session):
    return repositories.get_categories_tree(db)


def get_search_suggestions(db: Session, query: str, limit: int = 8):
    return repositories.get_search_suggestions(db, query, limit)


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


def get_products(db: Session, category_id: Optional[str] = None, search: Optional[str] = None, featured: Optional[bool] = None, sort_by: Optional[str] = None, product_type: Optional[str] = None, brand: Optional[str] = None, page: int = 1, limit: int = 20):
    items, total = repositories.get_products(db, category_id, search, featured, sort_by, product_type, brand, page, limit)
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


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


def group_specifications(specifications):
    grouped = {}
    for spec in specifications:
        grouped.setdefault(spec.group_name, []).append({
            "id": spec.id,
            "product_id": spec.product_id,
            "key": spec.spec_key,
            "value": spec.spec_value,
            "display_order": spec.display_order,
            "created_at": spec.created_at,
        })
    return grouped


def get_product_specifications(db: Session, product_id: str):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    return repositories.get_product_specifications(db, product_id)


def get_grouped_product_specifications(db: Session, product_id: str):
    return group_specifications(get_product_specifications(db, product_id))


def create_product_specification(db: Session, product_id: str, spec_data: dict):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    return repositories.create_product_specification(db, product_id, spec_data)


def update_product_specification(db: Session, specification_id: str, updates: dict):
    spec = repositories.get_product_specification(db, specification_id)
    if not spec:
        raise ValueError("Specification not found")
    return repositories.update_product_specification(db, spec, updates)


def delete_product_specification(db: Session, specification_id: str):
    spec = repositories.get_product_specification(db, specification_id)
    if not spec:
        raise ValueError("Specification not found")
    repositories.delete_product_specification(db, spec)


def replace_product_specifications(db: Session, product_id: str, specifications: list[dict]):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    normalized_specs = []
    for index, spec in enumerate(specifications):
        group_name = (spec.get("group_name") or "").strip()
        spec_key = (spec.get("spec_key") or "").strip()
        if not group_name or not spec_key:
            continue
        normalized_specs.append({
            "group_name": group_name,
            "spec_key": spec_key,
            "spec_value": spec.get("spec_value"),
            "display_order": spec.get("display_order", index),
        })
    return repositories.replace_product_specifications(db, product_id, normalized_specs)


def get_spec_templates(db: Session, product_type: str):
    return repositories.get_spec_templates(db, product_type)


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


def create_order(
    db: Session,
    user_id: str,
    items: list[dict],
    shipping_address: Optional[str] = None,
    payment_method: Optional[str] = None,
    address_id: Optional[str] = None,
    shipping_method: Optional[str] = None,
    shipping_fee: float = 0,
    order_note: Optional[str] = None,
):
    if not items:
        raise ValueError("Order must contain at least one item")

    address_record = None
    if address_id:
        address_record = repositories.get_address_by_id(db, address_id)
        if not address_record or address_record.user_id != user_id:
            raise ValueError("Invalid address selected")
        if not shipping_address:
            shipping_address = f"{address_record.full_name}, {address_record.street}, {address_record.district or ''}, {address_record.city}, {address_record.country}".replace(' ,', ',').strip(', ')

    estimated_delivery_days = None
    if shipping_method:
        shipping_config = {
            "standard": {"days": 3, "fee": 15000},
            "express": {"days": 1, "fee": 35000},
            "same_day": {"days": 0, "fee": 75000},
        }
        config = shipping_config.get(shipping_method)
        if config:
            estimated_delivery_days = config["days"]

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

    total_amount += shipping_fee

    order = repositories.create_order(
        db,
        user_id,
        total_amount,
        shipping_address,
        payment_method,
        address_id,
        shipping_method,
        shipping_fee,
        order_note,
        estimated_delivery_days,
    )

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


# Order Tracking Services
VALID_STATUS_TRANSITIONS = {
    "pending": ["confirmed", "cancelled", "payment_failed"],
    "confirmed": ["processing"],
    "processing": ["shipped"],
    "shipped": ["out_for_delivery"],
    "out_for_delivery": ["delivered"],
    "delivered": ["return_requested"],
    "return_requested": ["returned"],
    "returned": ["refunded"],
    "cancelled": [],
    "payment_failed": [],
    "refunded": [],
}


def update_order_status_with_history(db: Session, order_id: str, new_status: str, note: Optional[str] = None, changed_by: Optional[str] = None) -> models.Order:
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")

    old_status = order.status
    if new_status not in VALID_STATUS_TRANSITIONS.get(old_status, []):
        raise ValueError(f"Invalid status transition from {old_status} to {new_status}")

    # Update order status
    order = repositories.update_order_status(db, order, new_status)

    # Set timestamps based on status
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if new_status == "delivered":
        order.delivered_at = now
    elif new_status in ["cancelled", "payment_failed"]:
        order.cancelled_at = now
    elif new_status == "shipped":
        # Generate tracking info for shipped orders
        import random
        import string
        order.tracking_code = f"TK{random.randint(100000000, 999999999)}"
        order.shipping_provider = random.choice(["GHN", "GHTK", "Viettel Post", "FedEx"])
        order.estimated_delivery = now + timedelta(days=random.randint(2, 7))

    # Create history record
    repositories.create_order_status_history(db, order_id, old_status, new_status, note, changed_by)

    db.commit()
    return order


def get_order_tracking_timeline(db: Session, order_id: str) -> list[models.OrderStatusHistory]:
    return repositories.get_order_status_history(db, order_id)


def simulate_next_order_status(db: Session, order_id: str, changed_by: Optional[str] = None) -> models.Order:
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")

    current_status = order.status
    next_statuses = VALID_STATUS_TRANSITIONS.get(current_status, [])
    if not next_statuses:
        raise ValueError(f"No valid next status for {current_status}")

    # For simulation, pick the first valid next status
    next_status = next_statuses[0]
    return update_order_status_with_history(db, order_id, next_status, "Simulated status update", changed_by)


def get_admin_stats(db: Session):
    return {
        "total_products": repositories.get_product_count(db),
        "total_orders": repositories.get_order_count(db),
        "total_revenue": repositories.get_total_revenue(db),
        "total_users": repositories.get_user_count(db),
    }


# Product Variant Services
def get_product_variants(db: Session, product_id: str) -> list[models.ProductVariant]:
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return db.query(models.ProductVariant).filter(models.ProductVariant.product_id == product_id).order_by(models.ProductVariant.created_at).all()


def create_product_variant(db: Session, product_id: str, variant_data: dict) -> models.ProductVariant:
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")

    variant = models.ProductVariant(product_id=product_id, **variant_data)
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


def update_product_variant(db: Session, variant_id: str, variant_data: dict) -> models.ProductVariant:
    variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Variant not found")

    for key, value in variant_data.items():
        setattr(variant, key, value)

    db.commit()
    db.refresh(variant)
    return variant


def delete_product_variant(db: Session, variant_id: str):
    variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Variant not found")

    db.delete(variant)
    db.commit()

