from __future__ import annotations

from typing import Any

from sqlalchemy.orm import joinedload, Session

from app import models

SPEC_ALIASES = {
    "cpu": ["cpu", "chip", "processor", "chip xử lý", "bộ xử lý"],
    "gpu": ["gpu", "graphics", "card đồ họa", "vga"],
    "ram": ["ram", "memory", "bộ nhớ ram"],
    "storage": ["storage", "ssd", "hdd", "ổ cứng", "bộ nhớ trong", "lưu trữ"],
    "display": ["display", "screen", "màn hình", "độ phân giải", "kích thước màn hình"],
    "battery": ["battery", "pin", "thời lượng pin", "dung lượng pin"],
}


def product_query(db: Session):
    return (
        db.query(models.Product)
        .options(
            joinedload(models.Product.category),
            joinedload(models.Product.specifications),
        )
        .filter(models.Product.status == "active")
    )


def product_to_card(product: models.Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "image_url": product.image_url,
        "category": product.category.name if product.category else None,
        "rating": product.rating,
        "review_count": product.review_count,
        "stock": product.stock,
    }


def spec_map(product: models.Product) -> dict[str, str]:
    specs = {}
    for spec in product.specifications:
        key = (spec.spec_key or "").strip().lower()
        if key and spec.spec_value:
            specs[key] = spec.spec_value
    return specs


def find_spec_value(product: models.Product, field: str) -> str | None:
    aliases = SPEC_ALIASES.get(field, [field])
    specs = spec_map(product)
    for key, value in specs.items():
        if any(alias in key for alias in aliases):
            return value
    return None


def product_text(product: models.Product) -> str:
    spec_values = " ".join(
        f"{spec.group_name} {spec.spec_key} {spec.spec_value or ''}"
        for spec in product.specifications
    )
    category = product.category.name if product.category else ""
    return " ".join([
        product.name or "",
        product.brand or "",
        product.description or "",
        product.product_type or "",
        category,
        spec_values,
    ]).lower()


def match_products_by_terms(db: Session, terms: list[str], limit: int = 4) -> list[models.Product]:
    if not terms:
        return []
    products = product_query(db).all()
    scored = []
    for product in products:
        text = product_text(product)
        score = sum(1 for term in terms if term and term.lower() in text)
        if score:
            scored.append((score, product.rating or 0, product.review_count or 0, product))
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [item[3] for item in scored[:limit]]


# ---------------------------------------------------------------------------
# Functions migrated from chat_service.py
# ---------------------------------------------------------------------------

def spec_matches(spec_key: str) -> bool:
    """Return True if a spec key is deemed important for LLM context."""
    important_terms = (
        "cpu", "gpu", "ram", "pin", "battery", "camera", "display",
        "màn", "man", "chip", "storage", "ssd",
    )
    lowered = spec_key.lower()
    return any(term in lowered for term in important_terms)


def serialize_product(product: models.Product, db: Session) -> dict[str, Any]:
    """Build a rich product dict for LLM context (capped specs + primary variant)."""
    specs = (
        db.query(models.ProductSpecification)
        .filter(models.ProductSpecification.product_id == product.id)
        .order_by(models.ProductSpecification.display_order, models.ProductSpecification.created_at)
        .limit(12)
        .all()
    )
    selected_specs = [spec for spec in specs if spec_matches(spec.spec_key)][:6] or specs[:6]
    top_specs: dict[str, dict[str, str | None]] = {}
    for spec in selected_specs:
        top_specs.setdefault(spec.group_name, {})[spec.spec_key] = spec.spec_value

    variant = (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.product_id == product.id)
        .order_by(models.ProductVariant.is_default.desc(), models.ProductVariant.created_at)
        .first()
    )

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "rating": product.rating,
        "review_count": product.review_count,
        "product_type": product.product_type,
        "stock": product.stock,
        "image_url": product.image_url,
        "top_specs": top_specs,
        "variant_price": variant.price if variant else None,
        "variant": {
            "color_name": variant.color_name,
            "ram": variant.ram,
            "storage": variant.storage,
            "stock": variant.stock,
        } if variant else None,
    }


def product_cards_from_list(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build compact product cards for the ChatResponse."""
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "brand": p["brand"],
            "rating": p["rating"],
            "image_url": p.get("image_url"),
        }
        for p in products[:3]
    ]
