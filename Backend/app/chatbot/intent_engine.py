from __future__ import annotations

import json
import re
from typing import Any

from .base import ChatEngine
from .schemas import ChatContext, EngineResult, IntentResult
from .openrouter_formatter import openrouter_formatter as _formatter

# ---------------------------------------------------------------------------
# Regex-based detection (fallback when LLM classifier is unavailable)
# ---------------------------------------------------------------------------

BRANDS = [
    "apple", "asus", "samsung", "sony", "bose", "dell",
    "lenovo", "hp", "msi", "acer", "lg",
]

PRODUCT_HINTS = [
    "iphone", "macbook", "zenbook", "galaxy", "s24 ultra",
    "wh-1000xm5", "quietcomfort", "headphones", "earbuds",
    "laptop", "phone", "smartphone",
]

GPU_PATTERNS = [
    r"\brtx\s?\d{3,4}(?:\s?ti)?\b",
    r"\bgtx\s?\d{3,4}(?:\s?ti)?\b",
    r"\bradeon\s+(?:rx\s*)?\d{3,4}\b",
    r"\bintel\s+arc\s+\w+\b",
    r"\bm\d+\s?(?:pro|max|ultra)?\s+gpu\b",
]

CPU_PATTERNS = [
    r"\bintel\s+core\s+i[3579][-\s]?\d{3,5}[a-z]*\b",
    r"\bcore\s+i[3579][-\s]?\d{3,5}[a-z]*\b",
    r"\bamd\s+ryzen\s+[3579][-\s]?\d{3,5}[a-z]*\b",
    r"\bryzen\s+[3579][-\s]?\d{3,5}[a-z]*\b",
    r"\bapple\s+m[1234](?:\s?(?:pro|max|ultra))?\b",
    r"\bm[1234]\s?(?:pro|max|ultra)?\b",
]

GAME_NAMES = [
    "aaa games", "aaa", "valorant", "league of legends", "lol",
    "counter strike", "cs2", "pubg", "fortnite", "gta v", "gta 5",
    "cyberpunk", "elden ring", "minecraft", "dota 2",
    "genshin impact", "call of duty",
]

_INTENT_RULES = [
    (
        "compare_products",
        [r"\bcompare\b", r"\bcomparison\b", r"\bdifference between\b",
         r"\bvs\b", r"\bversus\b", r"\bwhich is better\b", r"\bso sánh\b"],
    ),
    (
        "gaming_capability",
        [r"\bcan .* run\b", r"\bplay .* game\b", r"\bgaming\b", r"\bfps\b",
         r"\brun .* smoothly\b", r"\bchơi game\b", r"\bchạy game\b"],
    ),
    (
        "recommend_product",
        [r"\brecommend\b", r"\bsuggest\b", r"\bbest\b", r"\bshould i buy\b",
         r"\bwhat .* buy\b", r"\btư vấn\b", r"\bgợi ý\b", r"\bnên mua\b"],
    ),
    (
        "spec_explanation",
        [r"\bwhat is\b", r"\bexplain\b", r"\bmeaning of\b", r"\bspec\b",
         r"\bspecification\b", r"\bthông số\b", r"\bgiải thích\b"],
    ),
    (
        "order_help",
        [r"\border\b", r"\bshipping\b", r"\bdelivery\b", r"\btracking\b",
         r"\breturn\b", r"\bcancel\b", r"\bđơn hàng\b", r"\bgiao hàng\b"],
    ),
    (
        "search_product",
        [r"\bfind\b", r"\bsearch\b", r"\bshow me\b", r"\bdo you have\b",
         r"\bavailable\b", r"\btìm\b", r"\bcó bán\b"],
    ),
]

# ---------------------------------------------------------------------------
# LLM-based classifier (primary, from chat_service.py)
# ---------------------------------------------------------------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
CLASSIFIER_MODEL = "meta-llama/llama-3.1-8b-instruct"

VALID_INTENTS = {
    "product_search", "product_compare", "gaming_check",
    "spec_query", "faq", "order_support", "recommendation",
    "chitchat", "greeting",
}

ENTITY_DEFAULTS: dict[str, Any] = {
    "product_type": None, "brand": None, "budget_max": None,
    "budget_min": None, "use_case": None, "game_name": None,
    "compare_products": [], "spec_query": None, "order_id": None,
}

_CLASSIFIER_SYSTEM_PROMPT = """
Ban la he thong phan loai intent cho shop ban dien tu (laptop, dien thoai,
tai nghe, phu kien). Phan tich tin nhan nguoi dung va tra ve JSON theo
dinh dang sau, KHONG them bat ky text nao ngoai JSON:

{
  "intent": "<ten intent>",
  "entities": {
    "product_type": "<laptop|phone|audio|tablet|accessory|null>",
    "brand": "<ten hang hoac null>",
    "budget_max": <so nguyen VND hoac null>,
    "budget_min": <so nguyen VND hoac null>,
    "use_case": "<gaming|work|study|photo|music|null>",
    "game_name": "<ten game hoac null>",
    "compare_products": ["<ten sp 1>", "<ten sp 2>"],
    "spec_query": "<cpu|gpu|ram|battery|camera|display|null>",
    "order_id": "<ma don hang hoac null>"
  }
}

Danh sach intent hop le:
- product_search    : tim kiem san pham cu the
- product_compare   : so sanh 2+ san pham
- gaming_check      : kiem tra chay game duoc khong
- spec_query        : hoi ve thong so ky thuat
- faq               : hoi chinh sach, bao hanh, van chuyen, doi tra
- order_support     : hoi don hang, trang thai, theo doi
- recommendation    : goi y san pham phu hop nhu cau
- chitchat          : hoi tham thuong, ngoai chu de
- greeting          : chao hoi, bat dau cuoc tro chuyen
""".strip()


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _find_regexes(patterns: list[str], message: str) -> list[str]:
    matches = []
    for pattern in patterns:
        matches.extend(match.group(0).strip()
                       for match in re.finditer(pattern, message, re.IGNORECASE))
    return _dedupe(matches)


def _find_terms(terms: list[str], normalized_message: str) -> list[str]:
    return [term for term in terms
            if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized_message)]


def _extract_price_ranges(message: str) -> list[dict[str, Any]]:
    normalized = message.lower()
    ranges = []
    between = re.compile(
        r"(?:between|from|từ)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?"
        r"\s*(?:to|and|đến|-)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )
    under = re.compile(
        r"(?:under|below|less than|dưới|không quá)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )
    over = re.compile(
        r"(?:over|above|more than|trên|hơn)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )
    for match in between.finditer(normalized):
        ranges.append({
            "min": _normalize_price(match.group(1), match.group(2) or match.group(4)),
            "max": _normalize_price(match.group(3), match.group(4) or match.group(2)),
            "raw": match.group(0),
        })
    for match in under.finditer(normalized):
        ranges.append({"min": None, "max": _normalize_price(match.group(1), match.group(2)), "raw": match.group(0)})
    for match in over.finditer(normalized):
        ranges.append({"min": _normalize_price(match.group(1), match.group(2)), "max": None, "raw": match.group(0)})
    return ranges


def _normalize_price(value: str, unit: str | None) -> int:
    amount = float(value.replace(",", "."))
    u = (unit or "").lower()
    if u in ("m", "million", "tr", "triệu"):
        amount *= 1_000_000
    elif u in ("k", "nghìn"):
        amount *= 1_000
    return int(amount)


def extract_entities_regex(message: str) -> dict[str, Any]:
    normalized = message.lower()
    return {
        "product_names": _find_terms(PRODUCT_HINTS, normalized),
        "brands": _find_terms(BRANDS, normalized),
        "gpus": _find_regexes(GPU_PATTERNS, message),
        "cpus": _find_regexes(CPU_PATTERNS, message),
        "games": _find_terms(GAME_NAMES, normalized),
        "price_ranges": _extract_price_ranges(message),
    }


def detect_intent_regex(message: str) -> IntentResult:
    normalized = message.lower().strip()
    entities = extract_entities_regex(message)

    for intent, patterns in _INTENT_RULES:
        if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
            return IntentResult(intent=intent, entities=entities, confidence=0.6)

    if entities["games"] or entities["gpus"]:
        return IntentResult(intent="gaming_capability", entities=entities, confidence=0.6)

    if entities["product_names"] or entities["brands"]:
        return IntentResult(intent="search_product", entities=entities, confidence=0.6)

    return IntentResult(intent="unknown", entities=entities, confidence=0.3)


# ---------------------------------------------------------------------------
# LLM classifier helpers (from chat_service.py)
# ---------------------------------------------------------------------------

def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in classifier response")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Classifier response is not an object")
    return data


def _normalize_intent_result(data: dict[str, Any]) -> IntentResult:
    intent = data.get("intent")
    if intent not in VALID_INTENTS:
        intent = "chitchat"

    entities = dict(ENTITY_DEFAULTS)
    raw_entities = data.get("entities") or {}
    if isinstance(raw_entities, dict):
        for key in entities:
            if key in raw_entities:
                entities[key] = raw_entities[key]

    if not isinstance(entities["compare_products"], list):
        entities["compare_products"] = []

    for key in ("budget_max", "budget_min"):
        value = entities.get(key)
        if value in ("", "null"):
            entities[key] = None
        elif value is not None:
            try:
                entities[key] = int(value)
            except (TypeError, ValueError):
                entities[key] = None

    return IntentResult(intent=intent, entities=entities, confidence=0.9)


def _call_llm_classifier(message: str, history: list[dict[str, str]]) -> dict[str, Any] | None:
    """Call OpenRouter classifier. Returns None on failure."""
    if not _formatter.enabled:
        return None

    classifier_messages = history[-6:] + [{"role": "user", "content": message}]
    try:
        raw = _formatter.call_openrouter_direct(
            system_prompt=_CLASSIFIER_SYSTEM_PROMPT,
            messages=classifier_messages,
            model=CLASSIFIER_MODEL,
            max_tokens=200,
            temperature=0.1,
        )
        return _extract_json_object(raw)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class IntentEngine(ChatEngine):
    """Orchestrates intent classification using LLM with regex fallback."""

    def handle(self, ctx: ChatContext) -> EngineResult:
        result = classify(ctx.message, ctx.history)
        ctx.intent_result = result
        return EngineResult(response_context={"intent_result": result})

    def actions_for(self, ctx: ChatContext) -> list[dict[str, str]]:
        if not ctx.intent_result:
            return []
        intent = ctx.intent_result.intent
        entities = ctx.intent_result.entities

        if intent == "product_search":
            product_type = entities.get("product_type") or ""
            url = f"/products?type={product_type}" if product_type else "/products"
            label = f"Xem tat ca {product_type}" if product_type else "Xem san pham"
            return [{"type": "navigate", "label": label, "url": url, "target": url}]
        if intent == "order_support":
            return [{"type": "navigate", "label": "Xem don hang", "url": "/profile?tab=orders", "target": "/profile?tab=orders"}]
        if intent == "faq":
            return [{"type": "navigate", "label": "Xem chinh sach", "url": "/policy", "target": "/policy"}]
        return []


intent_engine = IntentEngine()


def classify(message: str, history: list[dict[str, str]]) -> IntentResult:
    """Classify message intent. Uses LLM classifier first, falls back to regex."""
    result = _call_llm_classifier(message, history)
    if result is not None:
        return _normalize_intent_result(result)
    return detect_intent_regex(message)
