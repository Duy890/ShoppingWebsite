from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models
from app.chatbot.product_utils import product_query, product_to_card


def search_products(db: Session, query: str, entities: dict, limit: int = 6) -> list[dict]:
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
