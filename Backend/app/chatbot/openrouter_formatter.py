from __future__ import annotations

import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Any

import openai  # already in project requirements

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — reads from pydantic Settings (which loads .env automatically)
# ---------------------------------------------------------------------------
from app.core.config import settings as _app_settings

_API_KEY    = _app_settings.OPENROUTER_API_KEY or ""
_MODEL      = _app_settings.OPENROUTER_MODEL
_MAX_TOKENS = _app_settings.OPENROUTER_MAX_TOKENS
_SITE_URL   = _app_settings.SITE_URL
_SITE_NAME  = _app_settings.SITE_NAME

_MAX_HISTORY_TURNS = 6          # keep last N user+assistant pairs
_MAX_SPEC_CHARS    = 120        # truncate very long spec values
_MAX_PRODUCTS_IN_PROMPT = 5     # never dump more than this into the prompt


# ===========================================================================
# SYSTEM PROMPTS  (one per intent)
# ===========================================================================

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

    # -------------------------------------------------------------------
    "search_product": _BASE_RULES + """

## Your task — search_product
The backend has returned a list of matching products.
1. Briefly confirm what you found (product count, category).
2. Highlight the top 2-3 options with: name, price, one-line key spec summary, stock status.
3. If a product is out of stock, say so clearly.
4. Do NOT list every product if there are many — pick the most relevant ones.
""",

    # -------------------------------------------------------------------
    "recommend_product": _BASE_RULES + """

## Your task — recommend_product
The backend scored products against the user's use-case, budget, and brand preference.
1. Explain briefly *why* you are recommending each product (use-case fit, value for money).
2. Present up to 3 recommendations with: name, price, key strengths (2-3 bullets), \
any notable trade-off.
3. If a budget constraint was detected, acknowledge it explicitly.
4. Rank from most-recommended to least — the first product is your top pick.
5. Be opinionated but fair — users want a clear recommendation, not a list dump.
""",

    # -------------------------------------------------------------------
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

    # -------------------------------------------------------------------
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

    # -------------------------------------------------------------------
    "spec_explanation": _BASE_RULES + """

## Your task — spec_explanation
The user wants to understand a technical specification or term.
1. Explain the spec clearly in plain language (no jargon without explanation).
2. Give a practical example: "A laptop with X has enough RAM to..."
3. If the user mentioned a specific product, relate the explanation to that product's spec value.
4. Keep it short — 3-5 sentences is ideal for a spec explanation.
""",

    # -------------------------------------------------------------------
    "order_help": _BASE_RULES + """

## Your task — order_help
The user is asking about an order, shipping, return, or cancellation.
1. Acknowledge their request empathetically.
2. Provide whatever information is available in <backend_data>.
3. If no order data is available, direct them to the customer support channel \
and do NOT invent order statuses or tracking numbers.
4. Do NOT ask a follow-up question at the end — this is a support context.
""",

    # -------------------------------------------------------------------
    "unknown": _BASE_RULES + """

## Your task — unknown intent
The backend could not classify the user's request.
1. Politely acknowledge you did not fully understand the request.
2. Offer 2-3 concrete things you *can* help with (search, compare, recommend, gaming check).
3. Do NOT guess or make up information.
4. Do NOT ask a follow-up question — invite them to rephrase instead.
""",
}

# Fallback for any intent not listed above
_DEFAULT_SYSTEM_PROMPT = _INTENT_SYSTEM_PROMPTS["unknown"]


# ===========================================================================
# DATA SERIALISER  (keeps prompt lean)
# ===========================================================================

def _slim_product(p: dict[str, Any]) -> dict[str, Any]:
    """Keep only the fields the LLM needs; truncate long values."""
    keep = ["id", "name", "brand", "price", "category", "rating",
            "review_count", "stock"]
    out = {k: p[k] for k in keep if k in p and p[k] is not None}
    # Normalise price display
    if "price" in out and out["price"] is not None:
        out["price_display"] = f"{out['price']:,.0f} VND"
    return out


def _slim_spec_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """For compare_products: trim spec values, remove all-null fields."""
    slimmed: dict[str, Any] = {}
    for field, entries in fields.items():
        values = []
        for e in entries:
            val = e.get("value")
            if val is None:
                val = "Not specified"
            elif isinstance(val, str) and len(val) > _MAX_SPEC_CHARS:
                val = val[:_MAX_SPEC_CHARS] + "…"
            values.append({"product": e.get("product_name", "?"), "value": val})
        # Skip field if every product has "Not specified"
        if any(v["value"] != "Not specified" for v in values):
            slimmed[field] = values
    return slimmed


def _slim_evaluation(ev: dict[str, Any]) -> dict[str, Any]:
    """For gaming: strip verbose strengths/limitations to essentials."""
    out: dict[str, Any] = {}
    if "product" in ev:
        out["product"] = _slim_product(ev["product"])
    for key in ("capability", "strengths", "limitations", "gpu", "cpu", "ram_gb"):
        if key in ev and ev[key] is not None:
            out[key] = ev[key]
    return out


def _serialise_data(intent: str, data: Any) -> str:
    """
    Convert backend data to a compact JSON string suited for the LLM.
    Caps the number of products and removes nulls.
    """
    if data is None:
        return "null"

    try:
        if intent == "search_product" and isinstance(data, list):
            slim = [_slim_product(p) for p in data[:_MAX_PRODUCTS_IN_PROMPT]]
            return json.dumps(slim, ensure_ascii=False, indent=2)

        if intent == "recommend_product" and isinstance(data, list):
            slim = [_slim_product(p) for p in data[:_MAX_PRODUCTS_IN_PROMPT]]
            return json.dumps(slim, ensure_ascii=False, indent=2)

        if intent == "compare_products" and isinstance(data, dict):
            slim = {
                "products": [_slim_product(p) for p in data.get("products", [])],
                "fields":   _slim_spec_fields(data.get("fields", {})),
                "note":     data.get("note"),
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
                evaluated = [
                    _slim_evaluation(ev)
                    for ev in data["products"][:_MAX_PRODUCTS_IN_PROMPT]
                ]
                # When no game: keep only product card + raw hardware, drop
                # meaningless capability="unknown" entries
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
            # Only surface alternatives when a game is known AND adds value
            if has_game and data.get("alternatives"):
                slim["alternatives"] = [
                    _slim_product(p) for p in data["alternatives"][:3]
                ]
            if data.get("explanation"):
                slim["explanation"] = data["explanation"]
            return json.dumps(slim, ensure_ascii=False, indent=2)

        # Generic fallback: strip top-level None values
        if isinstance(data, dict):
            clean = {k: v for k, v in data.items() if v is not None}
            return json.dumps(clean, ensure_ascii=False, indent=2)

        return json.dumps(data, ensure_ascii=False, indent=2)

    except (TypeError, ValueError) as exc:
        logger.warning("Data serialisation failed: %s", exc)
        return str(data)[:500]


# ===========================================================================
# PROMPT BUILDER
# ===========================================================================

def _build_user_prompt(
    intent: str,
    entities: dict,
    data: Any,
    original_message: str,
    user_message: str | None,
) -> str:
    """
    Assembles the user-turn prompt with clearly separated sections
    so the model never confuses data with instructions.
    """
    data_block = _serialise_data(intent, data)

    # Compact entity summary (skip empty lists)
    entity_lines = []
    for key, val in entities.items():
        if val:
            entity_lines.append(f"  {key}: {json.dumps(val, ensure_ascii=False)}")
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
    """Keep last N complete turns (user + assistant pairs)."""
    if not history:
        return []
    # Ensure we have pairs
    pairs: list[dict] = []
    for msg in history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            pairs.append({"role": msg["role"], "content": str(msg["content"])[:800]})
    # Take last _MAX_HISTORY_TURNS * 2 messages
    return pairs[-(  _MAX_HISTORY_TURNS * 2):]


# ===========================================================================
# FORMATTER CLASS
# ===========================================================================

class OpenRouterFormatter:
    """Advanced LLM formatter using OpenRouter via the openai SDK."""

    def __init__(self) -> None:
        self.api_key = _API_KEY
        self.model   = _MODEL
        self.enabled = bool(self.api_key)
        self.client: openai.OpenAI | None = None

        if self.enabled:
            # OpenRouter is OpenAI-API-compatible — just point base_url at it.
            # Extra headers (Referer, X-Title) are passed per-request via
            # extra_headers so we never need to subclass the client.
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            logger.warning(
                "OpenRouterFormatter: OPENROUTER_API_KEY not set — "
                "formatter disabled, will return fallback messages."
            )

    # ------------------------------------------------------------------
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
        """
        Format a chatbot response via OpenRouter.

        Parameters
        ----------
        intent          : intent string from intent_engine.detect_intent()
        entities        : entities dict from intent_engine.extract_entities()
        data            : structured data from the matching engine
        original_message: plain-text fallback / pre-formatted message
        history         : (optional) list of previous {"role", "content"} dicts
        user_message    : (optional) raw user text (used verbatim in prompt)

        Returns
        -------
        Formatted markdown string, or original_message on failure.
        """
        if not self.enabled or self.client is None:
            return original_message

        system_prompt = _INTENT_SYSTEM_PROMPTS.get(intent, _DEFAULT_SYSTEM_PROMPT)
        system_prompt = system_prompt.replace("{site_name}", _SITE_NAME)

        user_prompt = _build_user_prompt(
            intent, entities, data, original_message, user_message
        )

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(_trim_history(history or []))
        messages.append({"role": "user", "content": user_prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,          # type: ignore[arg-type]
                temperature=0.3,
                max_tokens=_MAX_TOKENS,
                extra_headers={
                    "HTTP-Referer": _SITE_URL,
                    "X-Title":      _SITE_NAME,
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
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenRouter unexpected error: %s", exc)

        return original_message


# Module-level singleton
openrouter_formatter = OpenRouterFormatter()