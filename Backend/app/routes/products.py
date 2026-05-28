"""Product routes: CRUD, specs, variants, images, reviews, check-sku, spec-templates public."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, repositories, schemas
from ..services import product_service
from ..core.admin_security import log_admin_action
from ..core.database import get_db
from ..deps import get_current_user, get_optional_user, require_admin

router = APIRouter(tags=["products"])


# ── Product CRUD ──


@router.get("/products")
def read_products(
    category: str | None = None,
    search: str | None = None,
    featured: bool | None = None,
    sortBy: str | None = None,
    product_type: str | None = None,
    brand: str | None = None,
    page: int = 1,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    page = max(1, page)
    limit = min(max(1, limit), 100)
    result = product_service.get_products(db, category, search, featured, sortBy, product_type, brand, page, limit)
    if search and search.strip():
        user_id = current_user.id if current_user else None
        products_list = result.get("items", [])
        repositories.log_search(db, search, user_id, len(products_list))
    return result


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: str, db: Session = Depends(get_db)):
    try:
        product = product_service.get_product(db, product_id)
        repositories.increment_view_count(db, product_id)
        return product
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/products", response_model=schemas.ProductRead)
def create_product(payload: schemas.ProductCreate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    result = product_service.create_product(db, payload.dict())
    log_admin_action(
        db, current_user.id, "product.create", "product", result.id,
        details={"name": result.name, "sku": result.sku},
        ip_address=request.client.host if request.client else None,
    )
    return result


@router.put("/products/{product_id}", response_model=schemas.ProductRead)
def edit_product(product_id: str, payload: schemas.ProductUpdate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = product_service.update_product(db, product_id, payload.dict(exclude_none=True))
        log_admin_action(
            db, current_user.id, "product.update", "product", product_id,
            details={"changed_fields": [k for k, v in payload.dict(exclude_none=True).items() if v is not None]},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.update.failed", "product", product_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(product_id: str, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        product_service.delete_product(db, product_id)
        log_admin_action(
            db, current_user.id, "product.delete", "product", product_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.delete.failed", "product", product_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


# ── SKU Check ──


@router.get("/admin/check-sku")
def check_sku(
    sku: str,
    exclude_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Product).filter(
        func.lower(models.Product.sku) == sku.strip().lower()
    )
    if exclude_id:
        query = query.filter(models.Product.id != exclude_id)
    exists = db.query(query.exists()).scalar()
    return {"exists": exists, "sku": sku.strip()}


# ── Specifications ──


@router.get("/products/{product_id}/specifications")
def read_product_specifications(product_id: str, db: Session = Depends(get_db)):
    try:
        return product_service.get_grouped_product_specifications(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/products/{product_id}/specifications", response_model=schemas.ProductSpecificationRead)
def create_product_specification(product_id: str, payload: schemas.ProductSpecificationCreate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = product_service.create_product_specification(db, product_id, payload.dict())
        log_admin_action(
            db, current_user.id, "product.specification.create", "product", product_id,
            details={"spec_key": payload.spec_key, "group_name": payload.group_name},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.specification.create.failed", "product", product_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/products/{product_id}/specifications")
def replace_product_specifications(product_id: str, payload: schemas.ProductSpecificationBulkSave, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        specs = product_service.replace_product_specifications(db, product_id, [item.dict() for item in payload.specifications])
        log_admin_action(
            db, current_user.id, "product.specification.bulk_update", "product", product_id,
            details={"count": len(payload.specifications)},
            ip_address=request.client.host if request.client else None,
        )
        return product_service.group_specifications(specs)
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.specification.bulk_update.failed", "product", product_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/specifications/{specification_id}", response_model=schemas.ProductSpecificationRead)
def edit_product_specification(specification_id: str, payload: schemas.ProductSpecificationUpdate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = product_service.update_product_specification(db, specification_id, payload.dict(exclude_none=True))
        log_admin_action(
            db, current_user.id, "product.specification.update", "specification", specification_id,
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.specification.update.failed", "specification", specification_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/specifications/{specification_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_specification(specification_id: str, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        product_service.delete_product_specification(db, specification_id)
        log_admin_action(
            db, current_user.id, "product.specification.delete", "specification", specification_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.specification.delete.failed", "specification", specification_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


# ── Variants ──


@router.get("/products/{product_id}/variants", response_model=list[schemas.ProductVariantRead])
def get_product_variants(product_id: str, db: Session = Depends(get_db)):
    try:
        return product_service.get_product_variants(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/admin/products/{product_id}/variants", response_model=schemas.ProductVariantRead)
def create_product_variant(product_id: str, payload: schemas.ProductVariantCreate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = product_service.create_product_variant(db, product_id, payload.dict())
        log_admin_action(
            db, current_user.id, "product.variant.create", "product", product_id,
            details={"sku": result.sku, "color": result.color_name},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.variant.create.failed", "product", product_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/admin/variants/{variant_id}", response_model=schemas.ProductVariantRead)
def update_product_variant(variant_id: str, payload: schemas.ProductVariantUpdate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = product_service.update_product_variant(db, variant_id, payload.dict(exclude_none=True))
        log_admin_action(
            db, current_user.id, "product.variant.update", "variant", variant_id,
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.variant.update.failed", "variant", variant_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/admin/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(variant_id: str, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        product_service.delete_product_variant(db, variant_id)
        log_admin_action(
            db, current_user.id, "product.variant.delete", "variant", variant_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "product.variant.delete.failed", "variant", variant_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=404, detail=str(exc))


# ── Images ──


@router.get("/products/{product_id}/images", response_model=list[schemas.ProductImageRead])
def get_product_images(product_id: str, db: Session = Depends(get_db)):
    return repositories.get_product_images(db, product_id)


@router.put("/admin/products/{product_id}/images", response_model=list[schemas.ProductImageRead])
def update_product_images(
    product_id: str,
    images: list[schemas.ProductImageCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin(current_user)
    product = repositories.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    repositories.replace_product_images(db, product_id, [img.model_dump() for img in images])

    primary = next((img for img in images if img.is_primary), images[0] if images else None)
    if primary:
        product.image_url = primary.url
    db.commit()

    return repositories.get_product_images(db, product_id)


# ── Spec Templates (public read) ──


@router.get("/spec-templates/{product_type}", response_model=list[schemas.SpecTemplateRead])
def read_spec_templates(product_type: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return product_service.get_spec_templates(db, product_type)


# ── Reviews ──


@router.get("/products/{product_id}/reviews", response_model=list[schemas.ReviewRead])
def read_product_reviews(product_id: str, db: Session = Depends(get_db)):
    return product_service.get_product_reviews(db, product_id)


@router.post("/products/{product_id}/reviews", response_model=schemas.ReviewRead)
def create_product_review(product_id: str, payload: schemas.ReviewCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return product_service.create_review(db, current_user.id, product_id, payload.rating, payload.comment)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
