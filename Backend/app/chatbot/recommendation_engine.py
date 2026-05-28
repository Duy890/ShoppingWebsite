from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from .base import ChatEngine
from .schemas import ChatContext, EngineResult, ProductCard
from .product_utils import product_query, product_text, product_to_card


USE_CASE_TERMS = {
    "gaming": ["gaming", "game", "rtx", "gtx", "radeon", "gpu", "fps", "144hz", "240hz"],
    "office": ["office", "work", "business", "văn phòng", "excel", "word", "lightweight", "battery"],
    "creator": ["creator", "creative", "design", "render", "video", "photo", "studio", "oled", "m3", "gpu"],
    "ai_ml": ["ai", "ml", "machine learning", "cuda", "rtx", "gpu", "nvidia", "vram"],
}


class RecommendationEngine(ChatEngine):
    """Scoring-based product recommendation engine."""

    def handle(self, ctx: ChatContext) -> EngineResult:
        entities = ctx.intent_result.entities if ctx.intent_result else {}
        products = recommend_products(ctx.db, entities, ctx.message)
        product_cards = [
            ProductCard(**{k: v for k, v in p.items() if k in ProductCard.__dataclass_fields__})
            for p in products
        ]
        return EngineResult(
            recommendations=product_cards,
            response_context={"recommendation_data": products},
        )


recommendation_engine = RecommendationEngine()


def recommend_products(db: Session, entities: dict, message: str, limit: int = 5) -> list[dict]:
    price_range = _primary_price_range(entities)
    use_cases = _detect_use_cases(message)
    categories = [item.lower() for item in entities.get("product_names", [])]
    brands = [item.lower() for item in entities.get("brands", [])]

    products = product_query(db).all()
    scored = []
    for product in products:
        if price_range and not _within_budget(product.price, price_range):
            continue
        text = product_text(product)
        score = 0
        if product.featured:
            score += 2
        if product.rating:
            score += product.rating / 2
        if product.review_count:
            score += min(product.review_count / 100, 3)
        if brands and product.brand and product.brand.lower() in brands:
            score += 4
        if categories and any(category in text for category in categories):
            score += 3
        for use_case in use_cases:
            score += sum(1 for term in USE_CASE_TERMS[use_case] if term in text)
        if score > 0 or price_range:
            scored.append((score, product.rating or 0, product.review_count or 0, product))
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [product_to_card(item[3]) for item in scored[:limit]]


def _detect_use_cases(message: str) -> list[str]:
    normalized = message.lower()
    use_cases = []
    if any(term in normalized for term in ["gaming", "game", "fps", "chơi game"]):
        use_cases.append("gaming")
    if any(term in normalized for term in ["office", "work", "văn phòng", "học tập"]):
        use_cases.append("office")
    if any(term in normalized for term in ["creator", "design", "render", "video", "photo", "đồ họa"]):
        use_cases.append("creator")
    if any(term in normalized for term in ["ai", "ml", "machine learning", "deep learning", "cuda"]):
        use_cases.append("ai_ml")
    return use_cases


def _primary_price_range(entities: dict) -> dict | None:
    ranges = entities.get("price_ranges") or []
    return ranges[0] if ranges else None


def _within_budget(price: float, price_range: dict) -> bool:
    minimum = price_range.get("min")
    maximum = price_range.get("max")
    if minimum is not None and price < minimum:
        return False
    if maximum is not None and price > maximum:
        return False
    return True
