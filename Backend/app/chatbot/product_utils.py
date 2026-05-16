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
