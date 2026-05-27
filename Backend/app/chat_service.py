from __future__ import annotations

import json
import re
from collections import OrderedDict
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas
from .core.config import get_settings


def _get_openrouter_key() -> str:
    return get_settings().OPENROUTER_API_KEY or ""

def _get_chat_model() -> str:
    return get_settings().OPENROUTER_MODEL or "meta-llama/llama-3.1-8b-instruct"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
CLASSIFIER_MODEL = "meta-llama/llama-3.1-8b-instruct"

VALID_INTENTS = {
    "product_search",
    "product_compare",
    "gaming_check",
    "spec_query",
    "faq",
    "order_support",
    "recommendation",
    "chitchat",
    "greeting",
}

ENTITY_DEFAULTS: dict[str, Any] = {
    "product_type": None,
    "brand": None,
    "budget_max": None,
    "budget_min": None,
    "use_case": None,
    "game_name": None,
    "compare_products": [],
    "spec_query": None,
    "order_id": None,
}


class ConversationMemory:
    MAX_TURNS = 8
    MAX_SESSIONS = 500

    def __init__(self) -> None:
        self._sessions: OrderedDict[str, list[dict[str, str]]] = OrderedDict()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        history = self._sessions.get(session_id, [])
        if session_id in self._sessions:
            self._sessions.move_to_end(session_id)
        return list(history)

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        history = self._sessions.setdefault(session_id, [])
        history.extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ])
        max_messages = self.MAX_TURNS * 2
        if len(history) > max_messages:
            del history[: len(history) - max_messages]

        self._sessions.move_to_end(session_id)
        while len(self._sessions) > self.MAX_SESSIONS:
            self._sessions.popitem(last=False)

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def get_session_count(self) -> int:
        return len(self._sessions)


memory_store = ConversationMemory()


def _empty_entities() -> dict[str, Any]:
    return {**ENTITY_DEFAULTS, "compare_products": []}


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Classifier response is not an object")
    return data


def _normalize_intent_result(data: dict[str, Any]) -> dict[str, Any]:
    intent = data.get("intent")
    if intent not in VALID_INTENTS:
        intent = "chitchat"

    entities = _empty_entities()
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

    return {"intent": intent, "entities": entities}


def classify_intent(message: str, history: list[dict[str, str]]) -> dict[str, Any]:
    system_prompt = """
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

    classifier_messages = history[-6:] + [{"role": "user", "content": message}]
    try:
        raw = call_openrouter(
            system_prompt,
            classifier_messages,
            model=CLASSIFIER_MODEL,
            max_tokens=200,
            temperature=0.1,
        )
        return _normalize_intent_result(_extract_json_object(raw))
    except Exception:
        return {"intent": "chitchat", "entities": _empty_entities()}


def _spec_matches(spec_key: str) -> bool:
    important_terms = ("cpu", "gpu", "ram", "pin", "battery", "camera", "display", "màn", "man", "chip", "storage", "ssd")
    lowered = spec_key.lower()
    return any(term in lowered for term in important_terms)


def _serialize_product(product: models.Product, db: Session) -> dict[str, Any]:
    specs = (
        db.query(models.ProductSpecification)
        .filter(models.ProductSpecification.product_id == product.id)
        .order_by(models.ProductSpecification.display_order, models.ProductSpecification.created_at)
        .limit(12)
        .all()
    )
    selected_specs = [spec for spec in specs if _spec_matches(spec.spec_key)][:6] or specs[:6]
    top_specs: dict[str, dict[str, str | None]] = {}
    for spec in selected_specs:
        top_specs.setdefault(spec.group_name, {})[spec.spec_key] = spec.spec_value

    variant = (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.product_id == product.id)
        .order_by(models.ProductVariant.is_default.desc(), models.ProductVariant.created_at)
        .first()
    )

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "rating": product.rating,
        "review_count": product.review_count,
        "product_type": product.product_type,
        "stock": product.stock,
        "image_url": product.image_url,
        "top_specs": top_specs,
        "variant_price": variant.price if variant else None,
        "variant": {
            "color_name": variant.color_name,
            "ram": variant.ram,
            "storage": variant.storage,
            "stock": variant.stock,
        } if variant else None,
    }


def fetch_products_for_chat(db: Session, entities: dict[str, Any]) -> list[dict[str, Any]]:
    query = db.query(models.Product).filter(
        models.Product.status == "active",
        models.Product.stock > 0,
    )

    product_type = entities.get("product_type")
    if product_type:
        query = query.filter(models.Product.product_type == product_type)

    brand = entities.get("brand")
    if brand:
        query = query.filter(models.Product.brand.ilike(f"%{brand}%"))

    budget_max = entities.get("budget_max")
    if budget_max is not None:
        query = query.filter(models.Product.price <= budget_max)

    budget_min = entities.get("budget_min")
    if budget_min is not None:
        query = query.filter(models.Product.price >= budget_min)

    compare_names = [name for name in entities.get("compare_products", []) if name]
    if compare_names:
        name_filters = [models.Product.name.ilike(f"%{name}%") for name in compare_names]
        query = query.filter(or_(*name_filters))

    if entities.get("use_case") == "gaming":
        query = query.order_by(models.Product.rating.desc(), models.Product.review_count.desc())
    else:
        query = query.order_by(models.Product.featured.desc(), models.Product.rating.desc())

    return [_serialize_product(product, db) for product in query.limit(5).all()]


def fetch_benchmark_context(db: Session, entities: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    game_name = entities.get("game_name")
    if game_name:
        game = (
            db.query(models.GameRequirement)
            .filter(
                or_(
                    models.GameRequirement.game_name.ilike(f"%{game_name}%"),
                    models.GameRequirement.aliases.ilike(f"%{game_name}%"),
                )
            )
            .first()
        )
        if game:
            context["game"] = {
                "game_name": game.game_name,
                "aliases": game.aliases,
                "min": {
                    "gpu_score": game.min_gpu_score,
                    "cpu_score": game.min_cpu_score,
                    "ram_gb": game.min_ram_gb,
                },
                "recommended": {
                    "gpu_score": game.recommended_gpu_score,
                    "cpu_score": game.recommended_cpu_score,
                    "ram_gb": game.recommended_ram_gb,
                },
                "ultra": {
                    "gpu_score": game.ultra_gpu_score,
                    "cpu_score": game.ultra_cpu_score,
                    "ram_gb": game.ultra_ram_gb,
                },
            }

    if entities.get("product_type") == "laptop" or game_name:
        cpus = db.query(models.CpuBenchmark).order_by(models.CpuBenchmark.score.desc()).all()
        gpus = db.query(models.GpuBenchmark).order_by(models.GpuBenchmark.score.desc()).all()
        context["cpu_benchmarks"] = [
            {"name": item.name, "aliases": item.aliases, "score": item.score}
            for item in cpus
        ]
        context["gpu_benchmarks"] = [
            {"name": item.name, "aliases": item.aliases, "score": item.score}
            for item in gpus
        ]

    return context


def build_system_prompt(
    intent: str,
    entities: dict[str, Any],
    products: list[dict[str, Any]],
    benchmark_ctx: dict[str, Any],
    db_context: str,
) -> str:
    base = """
Ban la tro ly tu van cua shop dien tu. Phong cach: than thien, ngan gon,
chinh xac. Tra loi bang tieng Viet. Khong bao gio bia thong tin san pham.
Neu khong co du lieu, noi thang la shop chua co thong tin do.
""".strip()

    if intent in {"product_search", "recommendation"}:
        extra = f"""
Du lieu san pham hien co trong kho (chi dua vao danh sach nay, khong bia):
{json.dumps(products, ensure_ascii=False, indent=2)}

Gioi thieu 1-3 san pham phu hop nhat. Format: ten san pham, gia, diem noi bat.
Cuoi cung them cau hoi goi mo (VD: "Ban muon biet them ve mau sac hoac RAM?").
""".strip()
    elif intent == "product_compare":
        extra = f"""
Du lieu san pham de so sanh:
{json.dumps(products, ensure_ascii=False, indent=2)}

So sanh theo: gia, hieu nang chinh (CPU/chip), pin, man hinh, camera (neu co).
Ket luan nen chon cai nao tuy nhu cau cu the.
""".strip()
    elif intent == "gaming_check":
        extra = f"""
Thong tin yeu cau game va benchmark:
{json.dumps(benchmark_ctx, ensure_ascii=False, indent=2)}

Du lieu laptop hien co:
{json.dumps(products, ensure_ascii=False, indent=2)}

Ket luan xem laptop nao chay duoc game nay o muc nao (min/recommended/ultra).
Dua ra khuyen nghi ro rang.
""".strip()
    elif intent == "spec_query":
        extra = f"""
Du lieu san pham:
{json.dumps(products, ensure_ascii=False, indent=2)}

Tra loi chinh xac ve thong so duoc hoi. Neu spec khong co trong du lieu,
noi la "shop chua cap nhat thong so nay".
""".strip()
    elif intent == "faq":
        extra = """
Chinh sach cua shop:
- Bao hanh: 12 thang chinh hang, 3 thang phan phoi
- Doi tra: 7 ngay loi ky thuat, 1 ngay doi y (con nguyen hop)
- Van chuyen: Mien phi don tren 500.000 VND, giao 2-3 ngay
- Thanh toan: Hien chi ho tro COD (tra tien mat khi nhan hang)
- Ho tro: 8h-22h hang ngay, hotline 1800-xxxx
Tra loi dung chinh sach, ngan gon.
""".strip()
    elif intent == "order_support":
        extra = """
Huong dan nguoi dung vao trang "Tai khoan > Don hang cua toi" de xem
trang thai don hang. Neu ho cung cap ma don hang, bao rang ban khong
co quyen truy cap don hang truc tiep nhung co the huong dan ho.
""".strip()
    else:
        extra = """
Chao hoi than thien. Gioi thieu ban co the giup: tim san pham, so sanh,
tu van gaming, hoi chinh sach, kiem tra don hang.
""".strip()

    if db_context:
        extra = f"{extra}\n\nNgu canh bo sung tu database:\n{db_context}"

    return f"{base}\n\n{extra}\n\nEntities da phan tich: {json.dumps(entities, ensure_ascii=False)}"


def call_openrouter(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str | None = None,
    max_tokens: int = 600,
    temperature: float = 0.7,
) -> str:
    resolved_model = model or _get_chat_model()
    resolved_key = _get_openrouter_key()
    try:
        request = Request(
            OPENROUTER_URL,
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


def build_actions(intent: str, entities: dict[str, Any]) -> list[dict[str, str]]:
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


def _product_cards(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "brand": product["brand"],
            "rating": product["rating"],
            "image_url": product.get("image_url"),
        }
        for product in products[:3]
    ]


def process_chat_request(payload: schemas.ChatRequest, db: Session) -> schemas.ChatResponse:
    if not _get_openrouter_key():
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

    session_id = getattr(payload, "session_id", None) or "anonymous_default"
    history = memory_store.get_history(session_id)
    if not history and payload.history:
        history = [
            {"role": item.get("role", "user"), "content": str(item.get("content", ""))}
            for item in payload.history[-ConversationMemory.MAX_TURNS * 2:]
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ]

    intent_result = classify_intent(payload.message, history)
    intent = intent_result["intent"]
    entities = intent_result["entities"]

    products: list[dict[str, Any]] = []
    benchmark_ctx: dict[str, Any] = {}
    if intent in {"product_search", "recommendation", "product_compare", "spec_query", "gaming_check"}:
        products = fetch_products_for_chat(db, entities)
        benchmark_ctx = fetch_benchmark_context(db, entities)

    system_prompt = build_system_prompt(intent, entities, products, benchmark_ctx, "")
    messages = history + [{"role": "user", "content": payload.message}]
    response_text = call_openrouter(system_prompt, messages)
    memory_store.add_turn(session_id, payload.message, response_text)

    product_cards = _product_cards(products)
    return schemas.ChatResponse(
        intent=intent,
        entities=entities,
        message=response_text,
        products=product_cards,
        comparison={},
        gaming_result=benchmark_ctx if intent == "gaming_check" else {},
        recommendations=product_cards if intent == "recommendation" else [],
        actions=build_actions(intent, entities),
    )
