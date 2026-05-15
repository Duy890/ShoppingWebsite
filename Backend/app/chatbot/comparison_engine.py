from sqlalchemy.orm import Session

from app.chatbot.product_utils import find_spec_value, match_products_by_terms, product_to_card


COMPARE_FIELDS = ["price", "cpu", "gpu", "ram", "storage", "display", "battery"]


def compare_products(db: Session, entities: dict, message: str) -> dict:
    terms = []
    terms.extend(entities.get("product_names") or [])
    terms.extend(entities.get("brands") or [])
    terms.extend(_split_compare_terms(message))

    products = match_products_by_terms(db, terms, limit=2)
    if len(products) < 2:
        return {
            "products": [product_to_card(product) for product in products],
            "fields": {},
            "note": "Need at least two database products to compare.",
        }

    fields = {}
    for field in COMPARE_FIELDS:
        fields[field] = [
            {
                "product_id": product.id,
                "product_name": product.name,
                "value": _field_value(product, field),
            }
            for product in products
        ]

    return {
        "products": [product_to_card(product) for product in products],
        "fields": fields,
        "note": None,
    }


def _field_value(product, field: str):
    if field == "price":
        return product.price
    return find_spec_value(product, field) or "Not specified"


def _split_compare_terms(message: str) -> list[str]:
    lowered = message.lower()
    separators = [" vs ", " versus ", " compare ", " difference between ", " and "]
    terms = []
    for separator in separators:
        if separator in lowered:
            terms.extend(part.strip(" ?.,") for part in lowered.split(separator) if len(part.strip()) > 2)
    return terms
