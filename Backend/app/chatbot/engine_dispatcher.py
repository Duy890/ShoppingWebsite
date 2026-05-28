from __future__ import annotations

import logging
from typing import Any

from .base import ChatEngine
from .schemas import ChatContext, EngineResult
from .comparison_engine import ComparisonEngine, comparison_engine
from .gaming_engine import GamingEngine, gaming_engine
from .recommendation_engine import RecommendationEngine, recommendation_engine
from .search_engine import SearchEngine, search_engine

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent-to-engine mapping
# ---------------------------------------------------------------------------

_INTENT_MAP: dict[str, ChatEngine] = {
    "product_search": search_engine,
    "search_product": search_engine,
    "recommendation": recommendation_engine,
    "recommend_product": recommendation_engine,
    "product_compare": comparison_engine,
    "compare_products": comparison_engine,
    "gaming_check": gaming_engine,
    "gaming_capability": gaming_engine,
}

# Intents that do NOT need DB product fetching
_NON_PRODUCT_INTENTS = {
    "faq", "order_support", "order_help", "chitchat", "greeting",
    "spec_query", "spec_explanation", "unknown",
}


class EngineDispatcher:
    """Maps classified intent to the appropriate engine.

    Responsibilities:
    - Maintain intent→engine mapping
    - Fallback behavior for unknown intents
    - Provide a unified handle() entry point for the orchestration layer
    """

    def __init__(self) -> None:
        self._engines = dict(_INTENT_MAP)

    def get_engine(self, intent: str) -> ChatEngine | None:
        return self._engines.get(intent)

    def requires_products(self, intent: str) -> bool:
        return intent not in _NON_PRODUCT_INTENTS

    def handle(self, ctx: ChatContext) -> EngineResult:
        """Dispatch to the correct engine based on classified intent.

        Falls back gracefully: unknown intents return an empty result,
        and the formatter will generate a helpful "I don't understand" response.
        """
        intent = ctx.intent_result.intent if ctx.intent_result else "unknown"
        engine = self.get_engine(intent)

        if engine is not None:
            try:
                return engine.handle(ctx)
            except Exception as exc:
                logger.error("Engine %s failed for intent %s: %s", engine.__class__.__name__, intent, exc)
                return EngineResult(response_context={"error": str(exc)})

        return EngineResult(response_context={"intent": intent})

    def actions_for(self, ctx: ChatContext) -> list[dict[str, str]]:
        """Collect UI action suggestions from the matched engine."""
        intent = ctx.intent_result.intent if ctx.intent_result else "unknown"
        engine = self.get_engine(intent)
        if engine is not None:
            try:
                return engine.actions_for(ctx)
            except Exception:
                return []
        return []


engine_dispatcher = EngineDispatcher()
