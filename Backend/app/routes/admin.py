"""Admin routes: stats, analytics, audit logs, session management, spec template CRUD, generate AI description."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import Request

from .. import models, repositories, schemas
from ..services import analytics_service
from ..core.admin_security import admin_rate_limiter, log_admin_action
from ..core.database import get_db
from ..deps import get_current_user, require_admin


def check_admin_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    key = f"admin:{client_ip}"
    if not admin_rate_limiter.check(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many admin requests. Please slow down.",
        )


router = APIRouter(
    tags=["admin"],
    dependencies=[Depends(check_admin_rate_limit)],
)


# ── Stats / Revenue ──


@router.get("/admin/stats", response_model=schemas.AdminStats)
def admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return analytics_service.get_admin_stats(db)


@router.get("/admin/revenue/monthly")
def revenue_monthly(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return analytics_service.get_revenue_by_month(db)


@router.get("/admin/revenue/yearly")
def revenue_yearly(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return analytics_service.get_revenue_by_year(db)


# ── AI Description Generation ──


@router.post("/admin/generate-description", response_model=schemas.GenerateDescriptionResponse)
async def generate_product_description(
    request: schemas.GenerateDescriptionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    from ..chatbot.openrouter_formatter import openrouter_formatter

    if not openrouter_formatter.enabled:
        raise HTTPException(status_code=503, detail="AI service not configured. Set OPENROUTER_API_KEY in .env")

    product_data = request.product_data

    system_prompt = """You are a professional Vietnamese e-commerce copywriter specializing in electronics, gaming laptops, PCs, smartphones, and technology products.

STRICT RULES:
- ONLY use the provided product information.
- NEVER invent specifications, benchmarks, features, ports, materials, technologies, or performance claims.
- NEVER generate fake FPS, benchmark scores, battery life, or unsupported capabilities.
- If information is missing, omit it naturally instead of guessing.
- Keep technical accuracy and consistency.
- Use natural, fluent, professional Vietnamese.
- Optimize writing for SEO and customer readability.
- Focus on real customer benefits instead of exaggerated marketing language.

TASK:
Generate a complete Vietnamese e-commerce product description based ONLY on the provided structured product data.
The output must include:
1. Short product introduction (1-2 sentences, highlight the most important feature)
2. Key highlights in bullet points (4-6 bullets, each 10-20 words, factual only)
3. Detailed product description (3-5 paragraphs, professional, no repetition)
4. Gaming/performance summary if product_type is laptop or phone (empty string if not applicable)
5. SEO meta description under 160 characters

WRITING STYLE:
- Professional, Modern, Premium, Technology-focused
- Clear and persuasive, Human-like writing
- Vietnamese language throughout

OUTPUT FORMAT:
Return ONLY valid JSON, no markdown fences, no explanation:
{
  "short_description": "",
  "key_highlights": [],
  "full_description": "",
  "performance_summary": "",
  "seo_description": ""
}"""

    user_prompt = f"PRODUCT DATA:\n{json.dumps(product_data, ensure_ascii=False, indent=2)}"

    try:
        completion = openrouter_formatter.client.chat.completions.create(
            model=openrouter_formatter.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
            extra_headers={
                "HTTP-Referer": "https://techzone.vn",
                "X-Title": "TechZone Admin",
            },
            timeout=45,
        )
        raw = completion.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        result = json.loads(raw)
        return schemas.GenerateDescriptionResponse(**result)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# ── Analytics ──


@router.get("/admin/analytics/top-searches")
def top_searches(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    return repositories.get_top_searches(db, limit=20)


@router.get("/admin/analytics/top-viewed")
def top_viewed_products(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    products = (
        db.query(models.Product)
        .filter(models.Product.status == "active")
        .order_by(models.Product.view_count.desc())
        .limit(10)
        .all()
    )
    return [
        {"id": p.id, "name": p.name, "view_count": p.view_count,
         "rating": p.rating, "price": p.price}
        for p in products
    ]


@router.get("/admin/analytics/cart-abandonment")
def cart_abandonment(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    rows = (
        db.query(
            models.CartItem.product_id,
            func.count(models.CartItem.id).label("cart_count"),
        )
        .group_by(models.CartItem.product_id)
        .order_by(func.count(models.CartItem.id).desc())
        .limit(10)
        .all()
    )
    result = []
    for r in rows:
        p = db.query(models.Product).filter(
            models.Product.id == r.product_id
        ).first()
        order_count = (
            db.query(func.count(models.OrderItem.id))
            .filter(models.OrderItem.product_id == r.product_id)
            .scalar() or 0
        )
        if p:
            result.append({
                "id": p.id,
                "name": p.name,
                "cart_count": r.cart_count,
                "order_count": order_count,
                "abandonment_rate": round(
                    (r.cart_count - order_count) / r.cart_count * 100, 1
                ) if r.cart_count > 0 else 0,
            })
    return result


# ── Spec Templates (admin CRUD) ──


@router.get("/admin/spec-templates", response_model=list[schemas.SpecTemplateRead])
def admin_list_templates(
    product_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    if product_type:
        return repositories.get_spec_templates(db, product_type)
    return repositories.get_all_spec_templates(db)


@router.post("/admin/spec-templates", response_model=schemas.SpecTemplateRead)
def admin_create_template(
    payload: schemas.SpecTemplateCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    try:
        result = repositories.create_spec_template_with_check(db, payload.dict())
        log_admin_action(
            db, current_user.id, "spec_template.create", "spec_template", result.id,
            details={"product_type": payload.product_type, "group_name": payload.group_name, "spec_key": payload.spec_key},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as e:
        log_admin_action(
            db, current_user.id, "spec_template.create.failed", "spec_template", None,
            details={"error": str(e)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/admin/spec-templates/types", response_model=list[str])
def list_spec_template_types(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return repositories.get_distinct_spec_template_types(db)


@router.delete("/admin/spec-templates/type/{product_type}", status_code=204)
def delete_spec_template_type(
    product_type: str,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    deleted = repositories.delete_spec_template_type(db, product_type)
    if deleted == 0:
        log_admin_action(
            db, current_user.id, "spec_template.type.delete.failed", "spec_template", None,
            details={"error": "Template type not found", "product_type": product_type},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail="Template type not found")
    log_admin_action(
        db, current_user.id, "spec_template.type.delete", "spec_template", None,
        details={"product_type": product_type},
        ip_address=request.client.host if request.client else None,
    )


@router.delete("/admin/spec-templates/{template_id}")
def admin_delete_template(
    template_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    try:
        repositories.delete_spec_template(db, template_id)
        log_admin_action(
            db, current_user.id, "spec_template.delete", "spec_template", template_id,
            ip_address=request.client.host if request.client else None,
        )
        return {"ok": True}
    except ValueError as e:
        log_admin_action(
            db, current_user.id, "spec_template.delete.failed", "spec_template", template_id,
            details={"error": str(e)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/admin/spec-templates/reorder")
def admin_reorder_templates(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    repositories.reorder_spec_templates(db, payload["product_type"], payload["ids"])
    log_admin_action(
        db, current_user.id, "spec_template.reorder", "spec_template", None,
        details={"product_type": payload.get("product_type"), "template_count": len(payload.get("ids", []))},
        ip_address=request.client.host if request.client else None,
    )
    return {"ok": True}


# ── Audit Logs ──


@router.get("/admin/audit-logs", response_model=list[schemas.AuditLogRead])
def admin_audit_logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    return analytics_service.get_audit_logs(db, limit, offset)


# ── Session Management ──


@router.get("/admin/sessions")
def admin_list_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    tokens = (
        db.query(models.RefreshToken)
        .filter(
            models.RefreshToken.revoked.is_(False),
            models.RefreshToken.expires_at > datetime.utcnow(),
        )
        .order_by(models.RefreshToken.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "device_info": t.device_info,
            "ip_address": t.ip_address,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "expires_at": t.expires_at.isoformat() if t.expires_at else None,
        }
        for t in tokens
    ]


@router.delete("/admin/sessions/{session_id}")
def admin_revoke_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    repositories.revoke_refresh_token(db, session_id)
    log_admin_action(
        db, current_user.id, "revoke_session", "session", session_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True}
