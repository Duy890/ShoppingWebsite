from . import schemas
from sqlalchemy.orm import Session

from .chatbot.comparison_engine import compare_products
from .chatbot.gaming_engine import evaluate_gaming_capability
from .chatbot.intent_engine import detect_intent
from .chatbot.openai_formatter import openai_formatter
from .chatbot.recommendation_engine import recommend_products
from .chatbot.search_engine import search_products


MOCK_MESSAGES = {
    "recommend_product": "Here are database products that best match your request.",
    "compare_products": "Here is a database-backed comparison using stored product fields and specifications.",
    "gaming_capability": "Here is a rule-based gaming capability check using internal benchmark data only.",
    "search_product": "Here are products found in the catalog database.",
    "spec_explanation": "I can explain common electronics specs. Detailed spec explanation logic is not enabled yet.",
    "order_help": "I can help with order, delivery, tracking, return, and cancellation questions. Please open your profile to view order details.",
    "unknown": "I am not sure what you need yet. You can ask about products, comparisons, gaming capability, specifications, or orders.",
}


def process_chat_request(payload: schemas.ChatRequest, db: Session | None = None) -> schemas.ChatResponse:
    result = detect_intent(payload.message)
    intent = result["intent"]
    entities = result["entities"]
    products = []
    recommendations = []
    comparison = {}
    gaming_result = {}
    actions = []
    message = MOCK_MESSAGES[intent]

    if db and intent == "search_product":
        products = search_products(db, payload.message, entities)
        if not products:
            message = "I could not find matching products in the catalog database."

    if db and intent == "gaming_capability":
        gaming_result = evaluate_gaming_capability(db, entities, payload.message)
        products = [item["product"] for item in gaming_result.get("products", [])]
        recommendations = gaming_result.get("alternatives", [])
        if gaming_result.get("explanation"):
            message = gaming_result["explanation"]

    if db and intent == "recommend_product":
        recommendations = recommend_products(db, entities, payload.message)
        products = recommendations
        if not recommendations:
            message = "I could not find database products that match those constraints."

    if db and intent == "compare_products":
        comparison = compare_products(db, entities, payload.message)
        if comparison.get("note"):
            message = comparison["note"]

    if intent in {"recommend_product", "search_product", "compare_products"}:
        actions.append({"type": "navigate", "label": "Browse products", "target": "/products"})
    elif intent == "order_help":
        actions.append({"type": "navigate", "label": "View orders", "target": "/profile"})

    # AI formatting layer
    data_for_ai = {
        "products": products,
        "recommendations": recommendations,
        "comparison": comparison,
        "gaming_result": gaming_result,
    }

    final_message = openai_formatter.format_response(
        intent=intent,
        entities=entities,
        data=data_for_ai,
        original_message=message
    )

    return schemas.ChatResponse(
        intent=intent,
        entities=entities,
        message=final_message,
        products=products,
        comparison=comparison,
        gaming_result=gaming_result,
        recommendations=recommendations,
        actions=actions,
    )
