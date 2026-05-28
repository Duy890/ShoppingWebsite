from __future__ import annotations

import re
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models
from .base import ChatEngine
from .schemas import ChatContext, EngineResult, ProductCard
from .product_utils import find_spec_value, product_query, product_text, product_to_card
from .recommendation_engine import recommend_products


CAPABILITY_ORDER = ["low", "medium", "high", "ultra"]


class GamingEngine(ChatEngine):
    """Evaluates hardware capability against game requirements and benchmark data."""

    def handle(self, ctx: ChatContext) -> EngineResult:
        entities = ctx.intent_result.entities if ctx.intent_result else {}
        gaming_result = evaluate_gaming_capability(ctx.db, entities, ctx.message)
        product_cards = []
        for ev in gaming_result.get("products", []):
            p = ev.get("product", {})
            if p:
                product_cards.append(ProductCard(**{k: v for k, v in p.items()
                                                    if k in ProductCard.__dataclass_fields__}))
        return EngineResult(
            products=product_cards,
            gaming_result=gaming_result,
            response_context={"gaming_data": gaming_result},
        )


gaming_engine = GamingEngine()


# ---------------------------------------------------------------------------
# Legacy public API (kept for backward compatibility)
# ---------------------------------------------------------------------------

def evaluate_gaming_capability(db: Session, entities: dict, message: str, limit: int = 4) -> dict:
    game_requirement = _find_game_requirement(db, entities, message)
    direct_gpu = _find_gpu_benchmark(db, (entities.get("gpus") or [None])[0])
    direct_cpu = _find_cpu_benchmark(db, (entities.get("cpus") or [None])[0])

    evaluated_products = []
    products = _candidate_products(db, entities, message, limit)
    for product in products:
        evaluation = _evaluate_product(db, product, game_requirement)
        evaluated_products.append(evaluation)

    direct_evaluation = None
    if direct_gpu or direct_cpu:
        direct_evaluation = _evaluate_component_set(direct_gpu, direct_cpu, None, game_requirement)

    alternatives = recommend_products(db, entities, f"{message} gaming", limit=limit)

    return {
        "game": _game_payload(game_requirement),
        "direct_evaluation": direct_evaluation,
        "products": evaluated_products,
        "alternatives": alternatives,
        "explanation": _build_explanation(game_requirement, direct_evaluation, evaluated_products),
    }


# ---------------------------------------------------------------------------
# Benchmark context (migrated from chat_service.py)
# ---------------------------------------------------------------------------

def fetch_benchmark_context(db: Session, entities: dict[str, Any]) -> dict[str, Any]:
    """Fetch game requirements + benchmark data for the chat response."""
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
                "min": {"gpu_score": game.min_gpu_score, "cpu_score": game.min_cpu_score, "ram_gb": game.min_ram_gb},
                "recommended": {"gpu_score": game.recommended_gpu_score, "cpu_score": game.recommended_cpu_score, "ram_gb": game.recommended_ram_gb},
                "ultra": {"gpu_score": game.ultra_gpu_score, "cpu_score": game.ultra_cpu_score, "ram_gb": game.ultra_ram_gb},
            }

    if entities.get("product_type") == "laptop" or game_name:
        cpus = db.query(models.CpuBenchmark).order_by(models.CpuBenchmark.score.desc()).all()
        gpus = db.query(models.GpuBenchmark).order_by(models.GpuBenchmark.score.desc()).all()
        context["cpu_benchmarks"] = [{"name": item.name, "aliases": item.aliases, "score": item.score} for item in cpus]
        context["gpu_benchmarks"] = [{"name": item.name, "aliases": item.aliases, "score": item.score} for item in gpus]

    return context


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _candidate_products(db: Session, entities: dict, message: str, limit: int):
    terms = list(entities.get("product_names") or [])
    terms.extend(entities.get("brands") or [])
    normalized = message.lower()

    products = product_query(db).all()
    scored = []
    for product in products:
        text = product_text(product)
        score = 0
        score += sum(1 for term in terms if term.lower() in text)
        score += 3 if any(term in text for term in ["gaming", "rtx", "gtx", "radeon", "gpu"]) else 0
        if "laptop" in normalized and "laptop" in text:
            score += 2
        if score:
            scored.append((score, product.rating or 0, product.review_count or 0, product))
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [item[3] for item in scored[:limit]]


def _evaluate_product(db: Session, product: models.Product, requirement: models.GameRequirement | None) -> dict:
    gpu_text = find_spec_value(product, "gpu")
    cpu_text = find_spec_value(product, "cpu")
    ram_text = find_spec_value(product, "ram")
    gpu = _find_gpu_benchmark(db, gpu_text)
    cpu = _find_cpu_benchmark(db, cpu_text)
    ram_gb = _extract_ram_gb(ram_text)
    evaluation = _evaluate_component_set(gpu, cpu, ram_gb, requirement)
    return {
        "product": product_to_card(product),
        "gpu": _benchmark_payload(gpu),
        "cpu": _benchmark_payload(cpu),
        "ram_gb": ram_gb,
        **evaluation,
    }


def _evaluate_component_set(gpu, cpu, ram_gb: int | None, requirement) -> dict:
    if not requirement:
        return {"capability": "unknown", "strengths": [], "limitations": ["No matching game requirement exists in the internal database."]}
    levels = []
    strengths = []
    limitations = []
    if gpu:
        gpu_level = _score_level(gpu.score, requirement.min_gpu_score, requirement.recommended_gpu_score, requirement.ultra_gpu_score)
        levels.append(gpu_level)
        strengths.append(f"GPU matched internal benchmark: {gpu.name}.")
    else:
        limitations.append("GPU benchmark is missing from the internal database.")
    if cpu:
        cpu_level = _score_level(cpu.score, requirement.min_cpu_score, requirement.recommended_cpu_score, requirement.ultra_cpu_score)
        levels.append(cpu_level)
        strengths.append(f"CPU matched internal benchmark: {cpu.name}.")
    else:
        limitations.append("CPU benchmark is missing from the internal database.")
    if ram_gb is not None:
        ram_level = _ram_level(ram_gb, requirement)
        levels.append(ram_level)
        strengths.append(f"Detected {ram_gb}GB RAM.")
    else:
        limitations.append("RAM capacity is missing from product specifications.")
    capability = min(levels, key=lambda level: CAPABILITY_ORDER.index(level)) if levels else "unknown"
    if capability in {"low", "medium"}:
        limitations.append("Capability is limited by at least one stored requirement category.")
    return {"capability": capability, "strengths": strengths, "limitations": limitations}


def _score_level(score: int, minimum: int, recommended: int, ultra: int) -> str:
    if score >= ultra:
        return "ultra"
    if score >= recommended:
        return "high"
    if score >= minimum:
        return "medium"
    return "low"


def _ram_level(ram_gb: int, requirement: models.GameRequirement) -> str:
    if ram_gb >= requirement.ultra_ram_gb:
        return "ultra"
    if ram_gb >= requirement.recommended_ram_gb:
        return "high"
    if ram_gb >= requirement.min_ram_gb:
        return "medium"
    return "low"


def _find_gpu_benchmark(db: Session, value: str | None):
    return _find_benchmark(db, models.GpuBenchmark, value)


def _find_cpu_benchmark(db: Session, value: str | None):
    return _find_benchmark(db, models.CpuBenchmark, value)


def _find_benchmark(db: Session, model_type, value: str | None):
    if not value:
        return None
    normalized = value.lower()
    for row in db.query(model_type).all():
        candidates = [row.name.lower()]
        if row.aliases:
            candidates.extend(alias.strip().lower() for alias in row.aliases.split(","))
        if any(candidate and candidate in normalized for candidate in candidates):
            return row
    return None


def _find_game_requirement(db: Session, entities: dict, message: str):
    candidates = [*entities.get("games", []), message]
    normalized_candidates = " ".join(candidates).lower()
    for requirement in db.query(models.GameRequirement).all():
        names = [requirement.game_name.lower()]
        if requirement.aliases:
            names.extend(alias.strip().lower() for alias in requirement.aliases.split(","))
        if any(name and name in normalized_candidates for name in names):
            return requirement
    return None


def _extract_ram_gb(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(\d+)\s*gb", value.lower())
    return int(match.group(1)) if match else None


def _benchmark_payload(benchmark) -> dict | None:
    if not benchmark:
        return None
    return {"name": benchmark.name, "score": benchmark.score}


def _game_payload(requirement) -> dict | None:
    if not requirement:
        return None
    return {
        "name": requirement.game_name,
        "min_ram_gb": requirement.min_ram_gb,
        "recommended_ram_gb": requirement.recommended_ram_gb,
        "ultra_ram_gb": requirement.ultra_ram_gb,
    }


def _build_explanation(requirement, direct_evaluation, product_evaluations: list[dict]) -> str:
    if not requirement:
        return "No matching game requirement was found in the internal database, so capability is limited to detected hardware matches."
    if direct_evaluation:
        return f"Evaluated against internal requirements for {requirement.game_name}. No FPS estimate is generated."
    if product_evaluations:
        return f"Evaluated matching catalog products against internal requirements for {requirement.game_name}. No FPS estimate is generated."
    return f"Found internal requirements for {requirement.game_name}, but no matching catalog product or complete hardware set was detected."
