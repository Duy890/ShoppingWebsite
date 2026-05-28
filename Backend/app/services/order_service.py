from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .. import models, repositories
from ._common import VALID_STATUS_TRANSITIONS


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


def update_order_status(db: Session, order_id: str, new_status: str) -> models.Order:
    """Wrapper đơn giản — cập nhật trạng thái đơn hàng không ghi history."""
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")
    order = repositories.update_order_status(db, order, new_status)
    db.commit()
    return order


def update_order_status_with_history(db: Session, order_id: str, new_status: str, note: Optional[str] = None, changed_by: Optional[str] = None) -> models.Order:
    import random
    import string
    order = repositories.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")

    old_status = order.status
    if new_status not in VALID_STATUS_TRANSITIONS.get(old_status, []):
        raise ValueError(f"Invalid status transition from {old_status} to {new_status}")

    order = repositories.update_order_status(db, order, new_status)

    now = datetime.utcnow()
    if new_status == "delivered":
        order.delivered_at = now
    elif new_status in ["cancelled", "payment_failed"]:
        order.cancelled_at = now
    elif new_status == "shipped":
        order.tracking_code = f"TK{random.randint(100000000, 999999999)}"
        order.shipping_provider = random.choice(["GHN", "GHTK", "Viettel Post", "FedEx"])
        order.estimated_delivery = now + timedelta(days=random.randint(2, 7))

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

    next_status = next_statuses[0]
    return update_order_status_with_history(db, order_id, next_status, "Simulated status update", changed_by)
