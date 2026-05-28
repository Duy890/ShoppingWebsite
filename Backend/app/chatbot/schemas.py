from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductCard:
    id: str
    name: str
    price: float
    brand: str | None = None
    image_url: str | None = None
    category: str | None = None
    rating: float = 0.0
    review_count: int = 0
    stock: int = 0
    product_type: str | None = None
    top_specs: dict[str, dict[str, str | None]] = field(default_factory=dict)
    variant_price: float | None = None
    variant: dict[str, Any] | None = None


@dataclass
class IntentResult:
    intent: str
    entities: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class EngineResult:
    products: list[ProductCard] = field(default_factory=list)
    comparison: dict[str, Any] = field(default_factory=dict)
    gaming_result: dict[str, Any] = field(default_factory=dict)
    recommendations: list[ProductCard] = field(default_factory=list)
    actions: list[dict[str, str]] = field(default_factory=list)
    response_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatContext:
    message: str
    session_id: str
    history: list[dict[str, str]]
    db: Any = None

    intent_result: IntentResult | None = None
    engine_result: EngineResult | None = None
    raw_response: str = ""
