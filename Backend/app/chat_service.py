"""Chatbot orchestration service.

This module is the sole entry point for the /api/chat endpoint.
It coordinates the flow across the engine layers WITHOUT containing
intent-specific business logic.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from . import schemas
from .chatbot.engine_dispatcher import engine_dispatcher
from .chatbot.intent_engine import IntentEngine, intent_engine
from .chatbot.memory import ConversationMemory, memory_store
from .chatbot.openrouter_formatter import openrouter_formatter
from .chatbot.product_utils import product_cards_from_list
from .chatbot.schemas import ChatContext

logger = logging.getLogger(__name__)


def process_chat_request(payload: schemas.ChatRequest, db: Session) -> schemas.ChatResponse:
    """Orchestrate the full chatbot request lifecycle.

    Flow:
    1. Guard: check AI service availability
    2. Context: resolve session, history
    3. Classify: determine intent + extract entities
    4. Fetch: invoke engines to gather domain data
    5. Respond: format response via OpenRouter
    6. Persist: save to conversation memory
    7. Return: normalized ChatResponse
    """
    # ── 1. Availability guard ──
    if not openrouter_formatter.enabled:
        return schemas.ChatResponse(
            intent="unavailable",
            entities={},
            message="Chatbot hien dang bao tri. Vui long thu lai sau.",
            products=[],
            comparison={},
            gaming_result={},
            recommendations=[],
            actions=[],
        )

    # ── 2. Build context ──
    session_id = getattr(payload, "session_id", None) or "anonymous_default"
    history = _resolve_history(memory_store, session_id, payload.history)

    ctx = ChatContext(
        message=payload.message,
        session_id=session_id,
        history=history,
        db=db,
    )

    # ── 3. Classify intent ──
    intent_engine.handle(ctx)
    intent = ctx.intent_result.intent if ctx.intent_result else "unknown"
    entities = ctx.intent_result.entities if ctx.intent_result else {}

    # ── 4. Fetch domain data via engine dispatcher ──
    engine_result = engine_dispatcher.handle(ctx)

    # Build response context for the formatter
    products_raw = engine_result.response_context.get("products_raw", [])
    if not products_raw and engine_dispatcher.requires_products(intent):
        from .chatbot.search_engine import fetch_products_for_chat
        products_raw = fetch_products_for_chat(db, entities)

    gaming_raw = engine_result.response_context.get("gaming_data", None) or engine_result.gaming_result or {}
    comparison_raw = engine_result.response_context.get("comparison_data", None) or engine_result.comparison or {}
    recommendation_raw = engine_result.response_context.get("recommendation_data", None) or []

    # ── 5. Generate response via formatter ──
    response_data = _build_formatter_data(products_raw, gaming_raw, comparison_raw, recommendation_raw, intent)

    response_text = openrouter_formatter.format_response(
        intent=_map_intent_to_formatter(intent),
        entities=entities,
        data=response_data,
        original_message=_build_fallback_message(intent, products_raw, comparison_raw),
        history=history,
        user_message=payload.message,
    )

    # ── 6. Persist conversation ──
    memory_store.add_turn(session_id, payload.message, response_text)

    # ── 7. Build response ──
    actions = engine_dispatcher.actions_for(ctx)
    product_cards = product_cards_from_list(products_raw)

    return schemas.ChatResponse(
        intent=intent,
        entities=entities,
        message=response_text,
        products=product_cards,
        comparison=_build_comparison_response(comparison_raw),
        gaming_result=gaming_raw if intent in ("gaming_check", "gaming_capability") else {},
        recommendations=product_cards if intent in ("recommendation", "recommend_product") else recommendation_raw[:3],
        actions=actions,
    )


# ---------------------------------------------------------------------------
# Internal helpers — pure coordination, no business logic
# ---------------------------------------------------------------------------

def _resolve_history(
    memory: ConversationMemory,
    session_id: str,
    payload_history: list[dict[str, Any]] | None,
) -> list[dict[str, str]]:
    """Resolve conversation history: from memory or payload."""
    history = memory.get_history(session_id)
    if not history and payload_history:
        history = [
            {"role": item.get("role", "user"), "content": str(item.get("content", ""))}
            for item in payload_history[-ConversationMemory.MAX_TURNS * 2:]
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ]
    return history


def _build_formatter_data(
    products: list[dict[str, Any]],
    gaming: dict[str, Any],
    comparison: dict[str, Any],
    recommendations: list,
    intent: str,
) -> Any:
    """Select the right data payload for the formatter based on intent."""
    if intent in ("gaming_check", "gaming_capability"):
        return gaming or products
    if intent in ("product_compare", "compare_products"):
        return comparison or products
    if intent in ("recommendation", "recommend_product"):
        return recommendations or products
    # search_product, spec_query, and everything else → products
    return products


def _build_fallback_message(intent: str, products: list, comparison: dict) -> str:
    """Build a plain-text fallback if LLM is unavailable."""
    if intent in ("gaming_check", "gaming_capability"):
        return "I found some products for gaming. Can you tell me which games you want to play?"
    if intent in ("product_compare", "compare_products") and comparison:
        return "Here are the products I found for comparison."
    if products:
        return f"I found {len(products)} products matching your request."
    return "I couldn't find products matching your request."


def _build_comparison_response(comparison_raw: dict) -> dict:
    """Extract the public comparison payload (strip internal fields)."""
    if not comparison_raw:
        return {}
    return {
        "products": comparison_raw.get("products", []),
        "fields": comparison_raw.get("fields", {}),
        "note": comparison_raw.get("note"),
    }


def _map_intent_to_formatter(intent: str) -> str:
    """Map internal intent names to formatter intent names."""
    mapping = {
        "search_product": "search_product",
        "product_search": "search_product",
        "compare_products": "compare_products",
        "product_compare": "compare_products",
        "gaming_capability": "gaming_capability",
        "gaming_check": "gaming_capability",
        "recommend_product": "recommend_product",
        "recommendation": "recommend_product",
        "spec_query": "spec_explanation",
        "spec_explanation": "spec_explanation",
        "order_support": "order_help",
        "order_help": "order_help",
        "faq": "faq",
        "chitchat": "unknown",
        "greeting": "unknown",
    }
    return mapping.get(intent, "unknown")
