from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import openai

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_MAX_HISTORY_TURNS = 6
_MAX_SPEC_CHARS = 120
_MAX_PRODUCTS_IN_PROMPT = 5

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------------------------------------------------------
# System prompts (one per intent, from the original openrouter_formatter.py)
# ---------------------------------------------------------------------------

_BASE_RULES = """\
## Ground rules — follow at all times
- You are a knowledgeable, friendly sales assistant for {site_name}, an electronics store.
- Respond in the **same language** the customer used (Vietnamese or English). \
If the message mixes both languages, prefer Vietnamese.
- **Never invent** specs, prices, benchmark scores, or product names. \
Use ONLY what is in the <backend_data> block below.
- If <backend_data> is empty or has no results, say so clearly and suggest \
the customer search again or visit the store.
- Use Markdown: **bold** key specs, bullet lists for comparisons, \
code-block tables only when side-by-side comparison has 3+ rows.
- Keep responses concise — aim for 150-300 words unless the data justifies more.
- Never mention OpenRouter, GPT, or any AI service. You are the store's own assistant.
- Do not repeat the customer's question back to them word-for-word.
- End every response with one short, relevant follow-up question to help the customer \
narrow down their decision (unless the intent is order_help or unknown).\
"""

_INTENT_SYSTEM_PROMPTS: dict[str, str] = {
    "search_product": _BASE_RULES + """

## Your task — search_product
The backend has returned a list of matching products.
1. Briefly confirm what you found (product count, category).
2. Highlight the top 2-3 options with: name, price, one-line key spec summary, stock status.
3. If a product is out of stock, say so clearly.
4. Do NOT list every product if there are many — pick the most relevant ones.
5. When presenting RAM and Storage, use ONLY the values from top_specs in <backend_data>. \
Do NOT infer specs from the product name. If top_specs is empty or missing RAM/Storage, \
write 'Chưa có thông tin' instead of guessing.
""",

    "recommend_product": _BASE_RULES + """

## Your task — recommend_product
The backend scored products against the user's use-case, budget, and brand preference.
1. Explain briefly *why* you are recommending each product (use-case fit, value for money).
2. Present up to 3 recommendations with: name, price, key strengths (2-3 bullets), \
any notable trade-off.
3. If a budget constraint was detected, acknowledge it explicitly.
4. Rank from most-recommended to least — the first product is your top pick.
5. Be opinionated but fair — users want a clear recommendation, not a list dump.
6. When presenting RAM and Storage, use ONLY the values from top_specs in <backend_data>. \
Do NOT infer specs from the product name. If top_specs is empty or missing RAM/Storage, \
write 'Chưa có thông tin' instead of guessing.
""",

    "compare_products": _BASE_RULES + """

## Your task — compare_products
The backend extracted specs for two products side-by-side.
1. Open with a one-sentence verdict: which product wins *overall* and for whom.
2. Present a comparison table with fields: Price, CPU, GPU, RAM, Storage, Display, Battery.
   - For any field showing "Not specified", write "—" in the table.
3. After the table, write 2-3 sentences on key differentiators that the table cannot capture \
(e.g. build quality, ecosystem, value at this price tier).
4. Close with a recommendation matching the user's apparent use-case.

Format the table as Markdown:
| Spec | Product A | Product B |
|------|-----------|-----------|
""",

    "gaming_capability": _BASE_RULES + """

## Your task — gaming_capability
The backend evaluated hardware against internal benchmark scores.
Capability levels: low < medium < high < ultra.

### CASE A — no_game_specified = true (customer asked generally, not about a specific game)
This is the most important case to handle gracefully.
1. Give an honest general verdict on the product's gaming potential based on its GPU and CPU.
   - Check <backend_data> for the "products" list — find the product the customer named.
   - If the GPU/CPU benchmark is present, describe it in plain terms (e.g. "integrated graphics",
     "entry-level discrete GPU", "mid-range dedicated GPU").
   - Do NOT show capability="unknown" or any raw backend fields to the customer.
2. Be direct and honest. For example, a Surface Laptop with Intel integrated graphics:
   "The Microsoft Surface Laptop 7 is not designed for gaming. It uses integrated Intel graphics,
    which can handle light titles like Minecraft or League of Legends at low settings,
    but will struggle with demanding games."
3. Do NOT list the alternative gaming laptops (ASUS ROG, Lenovo Legion, etc.) unless the
   customer explicitly asked for alternatives. Showing them is confusing and off-topic.
4. End with a specific question: "Which games are you hoping to play?" — this lets the backend
   run a proper capability check next turn.

### CASE B — no_game_specified = false (a specific game was matched)
1. State clearly whether the hardware **can run** the game and at what level.
2. Name the product, then explain which component is the bottleneck if any.
3. Translate capability tiers into practical terms:
   - low    → "may struggle at low settings"
   - medium → "playable at medium settings, ~30–60 FPS range"
   - high   → "smooth at high settings, 60+ FPS"
   - ultra  → "maxed-out settings, well above 60 FPS"
   (Never cite exact FPS as a hard number — use ranges.)
4. If alternatives are provided AND they are clearly better, mention 1–2 briefly.
5. Never fabricate benchmark numbers not in <backend_data>.
""",

    "spec_explanation": _BASE_RULES + """

## Your task — spec_explanation
The user wants to understand a technical specification or term.
1. Explain the spec clearly in plain language (no jargon without explanation).
2. Give a practical example: "A laptop with X has enough RAM to..."
3. If the user mentioned a specific product, relate the explanation to that product's spec value.
4. Keep it short — 3-5 sentences is ideal for a spec explanation.
""",

    "order_help": _BASE_RULES + """

## Your task — order_help
The user is asking about an order, shipping, return, or cancellation.
1. Acknowledge their request empathetically.
2. Provide whatever information is available in <backend_data>.
3. If no order data is available, direct them to the customer support channel \
and do NOT invent order statuses or tracking numbers.
4. Do NOT ask a follow-up question at the end — this is a support context.
""",

    "unknown": _BASE_RULES + """

## Your task — unknown intent
The backend could not classify the user's request.
1. Politely acknowledge you did not fully understand the request.
2. Offer 2-3 concrete things you *can* help with (search, compare, recommend, gaming check).
3. Do NOT guess or make up information.
4. Do NOT ask a follow-up question — invite them to rephrase instead.
""",
}

_DEFAULT_SYSTEM_PROMPT = _INTENT_SYSTEM_PROMPTS["unknown"]


# ---------------------------------------------------------------------------
# Data serialisation
# ---------------------------------------------------------------------------

def _truncate_val(val: str | None, limit: int = 80) -> str | None:
    if val is None:
        return None
    return val if len(val) <= limit else val[:limit] + "\u2026"


def _slim_product(p: dict[str, Any]) -> dict[str, Any]:
    keep = ["id", "name", "brand", "price", "category", "rating", "review_count", "stock"]
    out = {k: p[k] for k in keep if k in p and p[k] is not None}
    if "price" in out and out["price"] is not None:
        out["price_display"] = f"{out['price']:,.0f} VND"
    top_specs = p.get("top_specs")
    if top_specs and isinstance(top_specs, dict):
        out["top_specs"] = {
            group: {key: _truncate_val(val) for key, val in specs.items()}
            for group, specs in top_specs.items()
        }
    return out


def _slim_spec_fields(fields: dict[str, Any]) -> dict[str, Any]:
    slimmed: dict[str, Any] = {}
    for field, entries in fields.items():
        values = []
        for e in entries:
            val = e.get("value")
            if val is None:
                val = "Not specified"
            elif isinstance(val, str) and len(val) > _MAX_SPEC_CHARS:
                val = val[:_MAX_SPEC_CHARS] + "\u2026"
            values.append({"product": e.get("product_name", "?"), "value": val})
        if any(v["value"] != "Not specified" for v in values):
            slimmed[field] = values
    return slimmed


def _slim_evaluation(ev: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "product" in ev:
        out["product"] = _slim_product(ev["product"])
    for key in ("capability", "strengths", "limitations", "gpu", "cpu", "ram_gb"):
        if key in ev and ev[key] is not None:
            out[key] = ev[key]
    return out


def _serialise_data(intent: str, data: Any) -> str:
    if data is None:
        return "null"
    try:
        if intent == "search_product" and isinstance(data, list):
            return json.dumps([_slim_product(p) for p in data[:_MAX_PRODUCTS_IN_PROMPT]], ensure_ascii=False, indent=2)
        if intent == "recommend_product" and isinstance(data, list):
            return json.dumps([_slim_product(p) for p in data[:_MAX_PRODUCTS_IN_PROMPT]], ensure_ascii=False, indent=2)
        if intent == "compare_products" and isinstance(data, dict):
            slim = {
                "products": [_slim_product(p) for p in data.get("products", [])],
                "fields": _slim_spec_fields(data.get("fields", {})),
                "note": data.get("note"),
            }
            return json.dumps(slim, ensure_ascii=False, indent=2)
        if intent == "gaming_capability" and isinstance(data, dict):
            slim: dict[str, Any] = {}
            has_game = bool(data.get("game"))
            slim["no_game_specified"] = not has_game
            if has_game:
                slim["game"] = data["game"]
            if data.get("direct_evaluation"):
                slim["direct_evaluation"] = _slim_evaluation(data["direct_evaluation"])
            if data.get("products"):
                evaluated = [_slim_evaluation(ev) for ev in data["products"][:_MAX_PRODUCTS_IN_PROMPT]]
                if not has_game:
                    cleaned = []
                    for ev in evaluated:
                        entry: dict[str, Any] = {}
                        if "product" in ev:
                            entry["product"] = ev["product"]
                        for hw in ("gpu", "cpu", "ram_gb"):
                            if ev.get(hw):
                                entry[hw] = ev[hw]
                        cleaned.append(entry)
                    slim["products"] = cleaned
                else:
                    slim["products"] = evaluated
            if has_game and data.get("alternatives"):
                slim["alternatives"] = [_slim_product(p) for p in data["alternatives"][:3]]
            if data.get("explanation"):
                slim["explanation"] = data["explanation"]
            return json.dumps(slim, ensure_ascii=False, indent=2)
        if isinstance(data, dict):
            return json.dumps({k: v for k, v in data.items() if v is not None}, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as exc:
        logger.warning("Data serialisation failed: %s", exc)
        return str(data)[:500]


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(
    intent: str,
    entities: dict,
    data: Any,
    original_message: str,
    user_message: str | None = None,
) -> str:
    data_block = _serialise_data(intent, data)
    entity_lines = [f"  {key}: {json.dumps(val, ensure_ascii=False)}" for key, val in entities.items() if val]
    entity_block = "\n".join(entity_lines) if entity_lines else "  (none detected)"
    raw_question = user_message or original_message or "(no message)"

    return f"""\
<customer_message>
{raw_question}
</customer_message>

<detected_entities>
{entity_block}
</detected_entities>

<backend_data intent="{intent}">
{data_block}
</backend_data>

<fallback_message>
{original_message}
</fallback_message>

Using the data above, write a response to the customer. \
Remember: only use facts from <backend_data>. \
If <backend_data> is empty or null, rely on <fallback_message> and tell the customer \
you couldn't find a match.\
"""


def _trim_history(history: list[dict]) -> list[dict]:
    if not history:
        return []
    pairs = [{"role": m["role"], "content": str(m.get("content", ""))[:800]}
             for m in history if m.get("role") in ("user", "assistant") and m.get("content")]
    return pairs[-(_MAX_HISTORY_TURNS * 2):]


def _get_system_prompt(intent: str, site_name: str) -> str:
    prompt = _INTENT_SYSTEM_PROMPTS.get(intent, _DEFAULT_SYSTEM_PROMPT)
    return prompt.replace("{site_name}", site_name)


# ---------------------------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------------------------

def _call_openrouter_urllib(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str | None = None,
    max_tokens: int = 600,
    temperature: float = 0.7,
) -> str:
    """Low-level OpenRouter call using urllib (used by classifier)."""
    settings = get_settings()
    resolved_model = model or settings.OPENROUTER_MODEL
    resolved_key = (settings.OPENROUTER_API_KEY or "").strip()
    if not resolved_key:
        return "Xin loi, chatbot dang bao tri."
    try:
        request = Request(
            _OPENROUTER_URL,
            data=json.dumps({
                "model": resolved_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
            }).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {resolved_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://eshop.local",
            },
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except HTTPError as exc:
        return f"Xin loi, co loi xay ra: OpenRouter HTTP {exc.code}"
    except URLError as exc:
        return f"Xin loi, co loi ket noi: {str(exc.reason)[:100]}"
    except Exception as exc:
        return f"Xin loi, co loi xay ra: {str(exc)[:100]}"


# ---------------------------------------------------------------------------
# Formatter class
# ---------------------------------------------------------------------------

class OpenRouterFormatter:
    """High-level formatter for chatbot responses via OpenRouter."""

    def __init__(self) -> None:
        self._cached_api_key: str | None = None
        self._cached_client: openai.OpenAI | None = None

    @property
    def api_key(self) -> str:
        return (get_settings().OPENROUTER_API_KEY or "").strip()

    @property
    def model(self) -> str:
        return get_settings().OPENROUTER_MODEL

    @property
    def max_tokens(self) -> int:
        return get_settings().OPENROUTER_MAX_TOKENS

    @property
    def site_url(self) -> str:
        return get_settings().SITE_URL

    @property
    def site_name(self) -> str:
        return get_settings().SITE_NAME

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    @property
    def client(self) -> openai.OpenAI | None:
        if not self.enabled:
            return None
        current_key = self.api_key
        if self._cached_client is None or self._cached_api_key != current_key:
            self._cached_api_key = current_key
            self._cached_client = openai.OpenAI(
                api_key=current_key,
                base_url="https://openrouter.ai/api/v1",
            )
        return self._cached_client

    def call_openrouter_direct(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        model: str | None = None,
        max_tokens: int = 200,
        temperature: float = 0.1,
    ) -> str:
        """Direct OpenRouter call via urllib (for classifier — no openai SDK dependency)."""
        return _call_openrouter_urllib(system_prompt, messages, model, max_tokens, temperature)

    def format_response(
        self,
        intent: str,
        entities: dict,
        data: Any,
        original_message: str,
        *,
        history: list[dict] | None = None,
        user_message: str | None = None,
    ) -> str:
        """Generate a natural-language response via OpenRouter.

        Returns markdown text on success, or *original_message* on failure
        (e.g. API key missing, network error).
        """
        client = self.client
        if not self.enabled or client is None:
            return original_message

        system_prompt = _get_system_prompt(intent, self.site_name)
        user_prompt = build_prompt(intent, entities, data, original_message, user_message)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(_trim_history(history or []))
        messages.append({"role": "user", "content": user_prompt})

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=self.max_tokens,
                extra_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.site_name,
                },
                timeout=30,
            )
            return completion.choices[0].message.content.strip()

        except openai.APITimeoutError:
            logger.error("OpenRouter request timed out (model=%s)", self.model)
        except openai.APIStatusError as exc:
            logger.error("OpenRouter API error %s: %s", exc.status_code, exc.message)
        except openai.APIConnectionError as exc:
            logger.error("OpenRouter connection error: %s", exc)
        except (AttributeError, IndexError, ValueError) as exc:
            logger.error("OpenRouter response parse error: %s", exc)
        except Exception as exc:
            logger.error("OpenRouter unexpected error: %s", exc)

        return original_message


openrouter_formatter = OpenRouterFormatter()
