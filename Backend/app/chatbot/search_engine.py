from __future__ import annotations

from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models
from .base import ChatEngine
from .schemas import ChatContext, EngineResult, ProductCard
from .product_utils import product_query, product_to_card, serialize_product


class SearchEngine(ChatEngine):
    """Product search with keyword matching + NLP normalization."""

    def handle(self, ctx: ChatContext) -> EngineResult:
        products = fetch_products_for_chat(ctx.db, ctx.intent_result.entities if ctx.intent_result else {})
        product_cards = [ProductCard(**{k: v for k, v in p.items() if k in ProductCard.__dataclass_fields__})
                         for p in products]
        return EngineResult(
            products=product_cards,
            response_context={"products_raw": products},
        )

    def actions_for(self, ctx: ChatContext) -> list[dict[str, str]]:
        if not ctx.intent_result:
            return []
        product_type = ctx.intent_result.entities.get("product_type") or ""
        url = f"/products?type={product_type}" if product_type else "/products"
        label = f"Xem tat ca {product_type}" if product_type else "Xem san pham"
        return [{"type": "navigate", "label": label, "url": url, "target": url}]


search_engine = SearchEngine()


def search_products(db: Session, query: str, entities: dict, limit: int = 6) -> list[dict]:
    """Legacy entry point — used by the dormant intent_engine dispatch pattern."""
    terms = _search_terms(query, entities)
    if not terms:
        return []

    filters = []
    for term in terms:
        value = f"%{term}%"
        filters.append(models.Product.name.ilike(value))
        filters.append(models.Product.brand.ilike(value))
        filters.append(models.Product.description.ilike(value))
        filters.append(models.Category.name.ilike(value))

    products = (
        product_query(db)
        .join(models.Category, isouter=True)
        .filter(or_(*filters))
        .order_by(models.Product.featured.desc(), models.Product.rating.desc(), models.Product.created_at.desc())
        .limit(limit)
        .all()
    )
    return [product_to_card(product) for product in products]


def _search_terms(query: str, entities: dict) -> list[str]:
    terms = []
    terms.extend(entities.get("product_names") or [])
    terms.extend(entities.get("brands") or [])
    terms.extend(entities.get("games") or [])

    cleaned_query = query.strip()
    if cleaned_query:
        terms.append(cleaned_query)

    seen = set()
    unique_terms = []
    for term in terms:
        key = term.lower()
        if key not in seen:
            seen.add(key)
            unique_terms.append(term)
    return unique_terms


# ---------------------------------------------------------------------------
# Migrated from chat_service.py — richer product fetch with entity-based filtering
# ---------------------------------------------------------------------------

DEFAULT_INTENTS_THAT_NEED_PRODUCTS = {
    "product_search", "recommendation", "product_compare",
    "recommend_product", "spec_query", "spec_explanation",
    "gaming_check", "gaming_capability",
}


def needs_products(intent: str) -> bool:
    return intent in DEFAULT_INTENTS_THAT_NEED_PRODUCTS


def fetch_products_for_chat(db: Session, entities: dict[str, Any]) -> list[dict[str, Any]]:
    """Rich product fetch with entity-based filtering (migrated from chat_service.py)."""
    use_case = entities.get("use_case")
    spec_query = entities.get("spec_query")

    # For gaming or GPU queries, prioritise laptops with a discrete GPU
    if use_case == "gaming" or (spec_query and spec_query.lower() == "gpu"):
        gpu_query = (
            db.query(models.Product)
            .join(models.ProductSpecification, models.Product.id == models.ProductSpecification.product_id)
            .filter(
                models.Product.status == "active",
                models.Product.stock > 0,
                models.Product.product_type == "laptop",
                models.ProductSpecification.spec_key.ilike("%gpu%"),
                ~models.ProductSpecification.spec_value.ilike("%integrated%"),
                ~models.ProductSpecification.spec_value.ilike("%M1%"),
                ~models.ProductSpecification.spec_value.ilike("%M2%"),
                ~models.ProductSpecification.spec_value.ilike("%M3%"),
            )
        )
        brand = entities.get("brand")
        if brand:
            gpu_query = gpu_query.filter(models.Product.brand.ilike(f"%{brand}%"))
        budget_max = entities.get("budget_max")
        if budget_max is not None:
            gpu_query = gpu_query.filter(models.Product.price <= budget_max)
        budget_min = entities.get("budget_min")
        if budget_min is not None:
            gpu_query = gpu_query.filter(models.Product.price >= budget_min)

        gpu_results = (
            gpu_query
            .order_by(models.Product.rating.desc(), models.Product.review_count.desc())
            .limit(5)
            .all()
        )
        if gpu_results:
            return [serialize_product(product, db) for product in gpu_results]
        # No results → fall through to the normal query below

    query = db.query(models.Product).filter(
        models.Product.status == "active",
        models.Product.stock > 0,
    )

    product_type = entities.get("product_type")
    if product_type:
        query = query.filter(models.Product.product_type == product_type)

    brand = entities.get("brand")
    if brand:
        query = query.filter(models.Product.brand.ilike(f"%{brand}%"))

    budget_max = entities.get("budget_max")
    if budget_max is not None:
        query = query.filter(models.Product.price <= budget_max)

    budget_min = entities.get("budget_min")
    if budget_min is not None:
        query = query.filter(models.Product.price >= budget_min)

    compare_names = [name for name in entities.get("compare_products", []) if name]
    if compare_names:
        name_filters = [models.Product.name.ilike(f"%{name}%") for name in compare_names]
        query = query.filter(or_(*name_filters))

    if use_case == "gaming":
        query = query.order_by(models.Product.rating.desc(), models.Product.review_count.desc())
    else:
        query = query.order_by(models.Product.featured.desc(), models.Product.rating.desc())

    return [serialize_product(product, db) for product in query.limit(5).all()]
