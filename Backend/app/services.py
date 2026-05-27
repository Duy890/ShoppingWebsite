import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

import requests as http_requests
from sqlalchemy.orm import Session

from . import models, repositories
from .core.config import get_settings
from .core.security import verify_password, hash_password, create_access_token as _create_access_token
from .core.email import send_email, build_reset_password_email, build_verify_email_change_email


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


def get_brands_by_category(db: Session, category_id: str | None = None):
    return repositories.get_brands_by_category(db, category_id)


def get_search_suggestions(db: Session, query: str, limit: int = 8):
    return repositories.get_search_suggestions(db, query, limit)


def create_category(
    db: Session,
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
):
    return repositories.create_category(db, name, description, parent_id)


def get_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    return category


def delete_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    if category.children:
        raise ValueError("Category has child categories and cannot be deleted")
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
            "unit": spec.get("unit"),
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


def get_revenue_by_month(db: Session) -> list[dict]:
    return repositories.get_revenue_by_month(db)


def get_revenue_by_year(db: Session) -> list[dict]:
    return repositories.get_revenue_by_year(db)


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


def _generate_unique_token(db: Session, model: type[models.Base]) -> str:
    for _ in range(5):
        token = secrets.token_urlsafe(32)
        if not db.query(model).filter(model.token == token).first():
            return token
    raise ValueError("Unable to generate secure token")


async def create_reset_token_and_send_email(db: Session, email: str) -> None:
    """
    Create a password reset token and send it to the user's email.
    Raises ValueError if the email is not registered.
    """
    user = repositories.get_user_by_email(db, email)
    if not user:
        raise ValueError("No account found with this email")

    token = _generate_unique_token(db, models.PasswordResetToken)
    reset_token = models.PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(reset_token)
    db.commit()

    reset_url = f"{get_settings().FRONTEND_URL}/reset-password?token={token}"
    html = build_reset_password_email(reset_url, user.full_name or "")
    await send_email(
        to=email,
        subject="Reset your password — Electronics Store",
        html_body=html,
    )


async def create_email_change_token_and_send(db: Session, user: models.User, new_email: str) -> None:
    """
    Create an email-change verification token and send it to the new address.
    Raises ValueError if new_email is already taken.
    """
    existing = repositories.get_user_by_email(db, new_email)
    if existing and existing.id != user.id:
        raise ValueError("This email is already registered to another account")

    token = _generate_unique_token(db, models.EmailChangeToken)
    email_token = models.EmailChangeToken(
        token=token,
        user_id=user.id,
        new_email=new_email,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(email_token)
    db.commit()

    verify_url = f"{get_settings().FRONTEND_URL}/verify-email-change?token={token}"
    html = build_verify_email_change_email(verify_url, new_email, user.full_name or "")
    await send_email(
        to=new_email,
        subject="Confirm your new email — Electronics Store",
        html_body=html,
    )


def confirm_email_change(db: Session, token: str) -> models.User:
    """Apply the email change after the user clicks the verification link."""
    email_token = (
        db.query(models.EmailChangeToken)
        .filter(models.EmailChangeToken.token == token, models.EmailChangeToken.used.is_(False))
        .first()
    )
    if not email_token:
        raise ValueError("Invalid or expired verification token")

    if datetime.utcnow() > email_token.expires_at:
        email_token.used = True
        db.commit()
        raise ValueError("Verification link has expired")

    user = repositories.get_user(db, email_token.user_id)
    if not user:
        raise ValueError("User not found")

    user.email = email_token.new_email
    email_token.used = True
    db.commit()
    db.refresh(user)
    return user


def create_reset_token(db: Session, email: str) -> str:
    user = repositories.get_user_by_email(db, email)
    if not user:
        raise ValueError("No account found with this email")
    token = _generate_unique_token(db, models.PasswordResetToken)
    reset_token = models.PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(reset_token)
    db.commit()
    return token


def reset_password(db: Session, token: str, new_password: str) -> models.User:
    reset_token = (
        db.query(models.PasswordResetToken)
        .filter(models.PasswordResetToken.token == token, models.PasswordResetToken.used.is_(False))
        .first()
    )
    if not reset_token:
        raise ValueError("Invalid or expired reset token")

    if datetime.utcnow() > reset_token.expires_at:
        reset_token.used = True
        db.commit()
        raise ValueError("Reset token has expired")

    user = repositories.get_user(db, reset_token.user_id)
    if not user:
        raise ValueError("User not found")
    user.hashed_password = hash_password(new_password)
    reset_token.used = True
    db.commit()
    db.refresh(user)
    return user


def create_momo_payment(amount: int, order_id: str, order_info: str) -> dict:
    s = get_settings()
    partner_code = s.MOMO_PARTNER_CODE
    access_key = s.MOMO_ACCESS_KEY
    secret_key = s.MOMO_SECRET_KEY
    redirect_url = s.MOMO_REDIRECT_URL
    ipn_url = s.MOMO_IPN_URL
    request_id = f"{order_id}_{uuid.uuid4().hex[:8]}"
    extra_data = ""
    request_type = "captureWallet"

    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={amount}"
        f"&extraData={extra_data}"
        f"&ipnUrl={ipn_url}"
        f"&orderId={order_id}"
        f"&orderInfo={order_info}"
        f"&partnerCode={partner_code}"
        f"&redirectUrl={redirect_url}"
        f"&requestId={request_id}"
        f"&requestType={request_type}"
    )

    signature = hmac.new(
        secret_key.encode("utf-8"),
        raw_signature.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    payload = {
        "partnerCode": partner_code,
        "requestType": request_type,
        "ipnUrl": ipn_url,
        "redirectUrl": redirect_url,
        "orderId": order_id,
        "amount": amount,
        "orderInfo": order_info,
        "requestId": request_id,
        "extraData": extra_data,
        "lang": "vi",
        "signature": signature,
    }

    try:
        response = http_requests.post(
            s.MOMO_ENDPOINT,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )
    except http_requests.exceptions.ConnectionError as e:
        raise ValueError(f"Cannot connect to MoMo gateway: {e}")
    except http_requests.exceptions.Timeout:
        raise ValueError("MoMo gateway timed out (>30s). Try again.")

    try:
        data = response.json()
    except Exception:
        raise ValueError(
            f"MoMo returned non-JSON response (HTTP {response.status_code}): {response.text[:200]}"
        )

    if data.get("resultCode", -1) != 0:
        raise ValueError(
            f"MoMo error {data.get('resultCode')}: {data.get('message', 'Unknown error')}"
        )

    return data


def verify_momo_ipn_signature(payload: dict) -> bool:
    s = get_settings()
    access_key = s.MOMO_ACCESS_KEY
    secret_key = s.MOMO_SECRET_KEY

    raw = (
        f"accessKey={access_key}"
        f"&amount={payload['amount']}"
        f"&extraData={payload['extraData']}"
        f"&message={payload['message']}"
        f"&orderId={payload['orderId']}"
        f"&orderInfo={payload['orderInfo']}"
        f"&orderType={payload['orderType']}"
        f"&partnerCode={payload['partnerCode']}"
        f"&payType={payload['payType']}"
        f"&requestId={payload['requestId']}"
        f"&responseTime={payload['responseTime']}"
        f"&resultCode={payload['resultCode']}"
        f"&transId={payload['transId']}"
    )

    expected = hmac.new(
        secret_key.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, payload.get("signature", ""))


def get_recommendations(
    db: Session,
    user_id: str | None = None,
    product_id: str | None = None,
    limit: int = 8,
) -> list[dict]:
    import math
    from sqlalchemy import func

    purchased_ids: set[str] = set()
    purchased_categories: set[str] = set()
    purchased_brands: set[str] = set()
    cart_product_ids: set[str] = set()
    wishlist_ids: set[str] = set()

    if user_id:
        orders = (
            db.query(models.OrderItem)
            .join(models.Order, models.Order.id == models.OrderItem.order_id)
            .join(models.Product, models.Product.id == models.OrderItem.product_id)
            .filter(
                models.Order.user_id == user_id,
                models.Order.status.notin_(["cancelled", "payment_failed"]),
            )
            .all()
        )
        for item in orders:
            purchased_ids.add(item.product_id)
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).first()
            if product:
                if product.category_id:
                    purchased_categories.add(product.category_id)
                if product.brand:
                    purchased_brands.add(product.brand.lower())

        cart = db.query(models.Cart).filter(
            models.Cart.user_id == user_id
        ).first()
        if cart:
            cart_items = db.query(models.CartItem).filter(
                models.CartItem.cart_id == cart.id
            ).all()
            cart_product_ids = {item.product_id for item in cart_items}

        wishlist_ids = set(
            repositories.get_wishlist_product_ids(db, user_id)
        )

    order_counts: dict[str, int] = {}
    rows = (
        db.query(
            models.OrderItem.product_id,
            func.count(models.OrderItem.id).label("cnt"),
        )
        .join(models.Order)
        .filter(models.Order.status.notin_(["cancelled", "payment_failed"]))
        .group_by(models.OrderItem.product_id)
        .all()
    )
    for r in rows:
        order_counts[r.product_id] = r.cnt

    cart_counts: dict[str, int] = {}
    rows = (
        db.query(
            models.CartItem.product_id,
            func.count(models.CartItem.id).label("cnt"),
        )
        .group_by(models.CartItem.product_id)
        .all()
    )
    for r in rows:
        cart_counts[r.product_id] = r.cnt

    products = (
        db.query(models.Product)
        .filter(
            models.Product.status == "active",
            models.Product.stock > 0,
        )
        .all()
    )

    scored: list[tuple[float, models.Product]] = []

    for product in products:
        if product_id and product.id == product_id:
            continue
        if product.id in purchased_ids:
            continue

        view_score = math.log(max(product.view_count or 0, 0) + 1)
        order_score = order_counts.get(product.id, 0) * 3.0
        cart_score = cart_counts.get(product.id, 0) * 1.5
        rating_score = (product.rating or 0) * 1.0
        popularity = view_score + order_score + cart_score + rating_score

        personal = 0.0
        if product.category_id in purchased_categories:
            personal += 5.0
        if product.brand and product.brand.lower() in purchased_brands:
            personal += 3.0
        if product.id in wishlist_ids:
            personal += 2.0

        abandoned = 4.0 if product.id in cart_product_ids else 0.0

        final_score = popularity + personal + abandoned

        if not user_id:
            final_score = popularity

        scored.append((final_score, product))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_products = [p for _, p in scored[:limit]]

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image_url": p.image_url,
            "brand": p.brand,
            "rating": p.rating,
            "review_count": p.review_count,
            "product_type": p.product_type,
            "category_id": p.category_id,
        }
        for p in top_products
    ]


def get_similar_products(
    db: Session,
    product_id: str,
    limit: int = 6,
) -> list[dict]:
    source = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not source:
        return []

    products = (
        db.query(models.Product)
        .filter(
            models.Product.status == "active",
            models.Product.stock > 0,
            models.Product.id != product_id,
        )
        .all()
    )

    scored = []
    for p in products:
        score = 0.0
        if source.category_id and p.category_id == source.category_id:
            score += 5.0
        if source.brand and p.brand and p.brand.lower() == source.brand.lower():
            score += 3.0
        if source.product_type and p.product_type == source.product_type:
            score += 2.0
        if source.price:
            price_ratio = p.price / source.price
            if 0.7 <= price_ratio <= 1.3:
                score += 2.0
        score += (p.rating or 0) * 0.5
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for _, p in scored[:limit]]
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image_url": p.image_url,
            "brand": p.brand,
            "rating": p.rating,
            "review_count": p.review_count,
            "product_type": p.product_type,
        }
        for p in top
    ]


def get_cart_recommendations(
    db: Session,
    user_id: str,
    limit: int = 4,
) -> list[dict]:
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()
    if not cart:
        return []

    cart_items = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).all()
    if not cart_items:
        return []

    cart_pids = {item.product_id for item in cart_items}

    from sqlalchemy import func as sqlfunc
    co_purchased: dict[str, int] = {}
    for pid in cart_pids:
        order_ids = (
            db.query(models.OrderItem.order_id)
            .filter(models.OrderItem.product_id == pid)
            .subquery()
        )
        rows = (
            db.query(
                models.OrderItem.product_id,
                sqlfunc.count(models.OrderItem.id).label("cnt"),
            )
            .filter(
                models.OrderItem.order_id.in_(order_ids),
                models.OrderItem.product_id.notin_(cart_pids),
            )
            .group_by(models.OrderItem.product_id)
            .all()
        )
        for r in rows:
            co_purchased[r.product_id] = (
                co_purchased.get(r.product_id, 0) + r.cnt
            )

    if co_purchased:
        top_pids = sorted(
            co_purchased, key=lambda pid: co_purchased[pid], reverse=True
        )[:limit]
        products = (
            db.query(models.Product)
            .filter(
                models.Product.id.in_(top_pids),
                models.Product.status == "active",
                models.Product.stock > 0,
            )
            .all()
        )
        if products:
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "image_url": p.image_url,
                    "brand": p.brand,
                    "rating": p.rating,
                }
                for p in products[:limit]
            ]

    category_ids = set()
    for pid in cart_pids:
        p = db.query(models.Product).filter(models.Product.id == pid).first()
        if p and p.category_id:
            category_ids.add(p.category_id)

    fallback = (
        db.query(models.Product)
        .filter(
            models.Product.category_id.in_(category_ids),
            models.Product.id.notin_(cart_pids),
            models.Product.status == "active",
            models.Product.stock > 0,
        )
        .order_by(models.Product.view_count.desc(), models.Product.rating.desc())
        .limit(limit)
        .all()
    )
    return [
        {"id": p.id, "name": p.name, "price": p.price,
         "image_url": p.image_url, "brand": p.brand, "rating": p.rating}
        for p in fallback
    ]

