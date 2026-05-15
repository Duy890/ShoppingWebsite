import re
from typing import Any


BRANDS = [
    "apple",
    "asus",
    "samsung",
    "sony",
    "bose",
    "dell",
    "lenovo",
    "hp",
    "msi",
    "acer",
    "lg",
]

PRODUCT_HINTS = [
    "iphone",
    "macbook",
    "zenbook",
    "galaxy",
    "s24 ultra",
    "wh-1000xm5",
    "quietcomfort",
    "headphones",
    "earbuds",
    "laptop",
    "phone",
    "smartphone",
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
    "aaa games",
    "aaa",
    "valorant",
    "league of legends",
    "lol",
    "counter strike",
    "cs2",
    "pubg",
    "fortnite",
    "gta v",
    "gta 5",
    "cyberpunk",
    "elden ring",
    "minecraft",
    "dota 2",
    "genshin impact",
    "call of duty",
]

INTENT_RULES = [
    (
        "compare_products",
        [
            r"\bcompare\b",
            r"\bcomparison\b",
            r"\bdifference between\b",
            r"\bvs\b",
            r"\bversus\b",
            r"\bwhich is better\b",
            r"\bso sánh\b",
        ],
    ),
    (
        "gaming_capability",
        [
            r"\bcan .* run\b",
            r"\bplay .* game\b",
            r"\bgaming\b",
            r"\bfps\b",
            r"\brun .* smoothly\b",
            r"\bchơi game\b",
            r"\bchạy game\b",
        ],
    ),
    (
        "recommend_product",
        [
            r"\brecommend\b",
            r"\bsuggest\b",
            r"\bbest\b",
            r"\bshould i buy\b",
            r"\bwhat .* buy\b",
            r"\btư vấn\b",
            r"\bgợi ý\b",
            r"\bnên mua\b",
        ],
    ),
    (
        "spec_explanation",
        [
            r"\bwhat is\b",
            r"\bexplain\b",
            r"\bmeaning of\b",
            r"\bspec\b",
            r"\bspecification\b",
            r"\bthông số\b",
            r"\bgiải thích\b",
        ],
    ),
    (
        "order_help",
        [
            r"\border\b",
            r"\bshipping\b",
            r"\bdelivery\b",
            r"\btracking\b",
            r"\breturn\b",
            r"\bcancel\b",
            r"\bđơn hàng\b",
            r"\bgiao hàng\b",
        ],
    ),
    (
        "search_product",
        [
            r"\bfind\b",
            r"\bsearch\b",
            r"\bshow me\b",
            r"\bdo you have\b",
            r"\bavailable\b",
            r"\btìm\b",
            r"\bcó bán\b",
        ],
    ),
]


def _find_regexes(patterns: list[str], message: str) -> list[str]:
    matches = []
    for pattern in patterns:
        matches.extend(match.group(0).strip() for match in re.finditer(pattern, message, re.IGNORECASE))
    return _dedupe(matches)


def _find_terms(terms: list[str], normalized_message: str) -> list[str]:
    return [term for term in terms if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized_message)]


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _extract_price_ranges(message: str) -> list[dict[str, Any]]:
    normalized = message.lower()
    ranges = []

    between_pattern = re.compile(
        r"(?:between|from|từ)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?\s*(?:to|and|đến|-)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )
    under_pattern = re.compile(
        r"(?:under|below|less than|dưới|không quá)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )
    over_pattern = re.compile(
        r"(?:over|above|more than|trên|hơn)\s*(\d+(?:[.,]\d+)?)\s*(m|million|tr|triệu|k|nghìn|vnd|đ|d|usd|\$)?",
        re.IGNORECASE,
    )

    for match in between_pattern.finditer(normalized):
        ranges.append({
            "min": _normalize_price(match.group(1), match.group(2) or match.group(4)),
            "max": _normalize_price(match.group(3), match.group(4) or match.group(2)),
            "raw": match.group(0),
        })

    for match in under_pattern.finditer(normalized):
        ranges.append({
            "min": None,
            "max": _normalize_price(match.group(1), match.group(2)),
            "raw": match.group(0),
        })

    for match in over_pattern.finditer(normalized):
        ranges.append({
            "min": _normalize_price(match.group(1), match.group(2)),
            "max": None,
            "raw": match.group(0),
        })

    return ranges


def _normalize_price(value: str, unit: str | None) -> int:
    amount = float(value.replace(",", "."))
    normalized_unit = (unit or "").lower()

    if normalized_unit in ["m", "million", "tr", "triệu"]:
        amount *= 1_000_000
    elif normalized_unit in ["k", "nghìn"]:
        amount *= 1_000

    return int(amount)


def extract_entities(message: str) -> dict[str, Any]:
    normalized = message.lower()
    return {
        "product_names": _find_terms(PRODUCT_HINTS, normalized),
        "brands": _find_terms(BRANDS, normalized),
        "gpus": _find_regexes(GPU_PATTERNS, message),
        "cpus": _find_regexes(CPU_PATTERNS, message),
        "games": _find_terms(GAME_NAMES, normalized),
        "price_ranges": _extract_price_ranges(message),
    }


def detect_intent(message: str) -> dict[str, Any]:
    normalized = message.lower().strip()
    entities = extract_entities(message)

    for intent, patterns in INTENT_RULES:
        if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
            return {
                "intent": intent,
                "entities": entities,
            }

    if entities["games"] or entities["gpus"]:
        return {
            "intent": "gaming_capability",
            "entities": entities,
        }

    if entities["product_names"] or entities["brands"]:
        return {
            "intent": "search_product",
            "entities": entities,
        }

    return {
        "intent": "unknown",
        "entities": entities,
    }
