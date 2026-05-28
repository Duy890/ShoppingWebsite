from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from .base import ChatEngine
from .schemas import ChatContext, EngineResult, ProductCard
from .product_utils import find_spec_value, match_products_by_terms, product_to_card
from .search_engine import fetch_products_for_chat


COMPARE_FIELDS = ["price", "cpu", "gpu", "ram", "storage", "display", "battery"]


class ComparisonEngine(ChatEngine):
    """Side-by-side product comparison with spec extraction."""

    def handle(self, ctx: ChatContext) -> EngineResult:
        entities = ctx.intent_result.entities if ctx.intent_result else {}
        result = compare_products(ctx.db, entities, ctx.message)
        product_cards = [
            ProductCard(**{k: v for k, v in p.items() if k in ProductCard.__dataclass_fields__})
            for p in result.get("products", [])
        ]
        return EngineResult(
            products=product_cards,
            comparison=result,
            response_context={"comparison_data": result},
        )


comparison_engine = ComparisonEngine()


def compare_products(db: Session, entities: dict, message: str) -> dict:
    """Compare up to 2 products, extracting spec fields side-by-side.

    Uses the legacy product-utils matching approach (from the original
    chatbot/comparison_engine.py) and ALSO tries the entity-based
    fetch from chat_service.py as enrichment.
    """
    terms = list(entities.get("product_names") or [])
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
