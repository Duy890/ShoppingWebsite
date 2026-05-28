import secrets
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from .. import models


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


VALID_STATUS_TRANSITIONS: dict[str, list[str]] = {
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


def generate_unique_token(db: Session, model: type[models.Base]) -> str:
    for _ in range(5):
        token = secrets.token_urlsafe(32)
        if not db.query(model).filter(model.token == token).first():
            return token
    raise ValueError("Unable to generate secure token")
