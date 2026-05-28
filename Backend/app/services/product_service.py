from typing import Optional

from sqlalchemy.orm import Session

from .. import models, repositories
from ._common import group_specifications


def get_products(db: Session, category_id: Optional[str] = None, search: Optional[str] = None, featured: Optional[bool] = None, sort_by: Optional[str] = None, product_type: Optional[str] = None, brand: Optional[str] = None, page: int = 1, limit: int = 20):
    items, total = repositories.get_products(db, category_id, search, featured, sort_by, product_type, brand, page, limit)
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


def get_product(db: Session, product_id: str):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return product


def create_product(db: Session, product_data: dict):
    return repositories.create_product(db, product_data)


def update_product(db: Session, product_id: str, updates: dict):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.update_product(db, product, updates)


def delete_product(db: Session, product_id: str):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    repositories.delete_product(db, product)


def get_product_specifications(db: Session, product_id: str):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    return repositories.get_product_specifications(db, product_id)


def get_grouped_product_specifications(db: Session, product_id: str):
    return group_specifications(get_product_specifications(db, product_id))


def create_product_specification(db: Session, product_id: str, spec_data: dict):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    return repositories.create_product_specification(db, product_id, spec_data)


def update_product_specification(db: Session, specification_id: str, updates: dict):
    spec = repositories.get_product_specification(db, specification_id)
    if not spec:
        raise ValueError("Specification not found")
    return repositories.update_product_specification(db, spec, updates)


def delete_product_specification(db: Session, specification_id: str):
    spec = repositories.get_product_specification(db, specification_id)
    if not spec:
        raise ValueError("Specification not found")
    repositories.delete_product_specification(db, spec)


def replace_product_specifications(db: Session, product_id: str, specifications: list[dict]):
    if not repositories.get_product(db, product_id):
        raise ValueError("Product not found")
    normalized_specs = []
    for index, spec in enumerate(specifications):
        group_name = (spec.get("group_name") or "").strip()
        spec_key = (spec.get("spec_key") or "").strip()
        if not group_name or not spec_key:
            continue
        normalized_specs.append({
            "group_name": group_name,
            "spec_key": spec_key,
            "spec_value": spec.get("spec_value"),
            "unit": spec.get("unit"),
            "display_order": spec.get("display_order", index),
        })
    return repositories.replace_product_specifications(db, product_id, normalized_specs)


def get_spec_templates(db: Session, product_type: str):
    return repositories.get_spec_templates(db, product_type)


def get_product_reviews(db: Session, product_id: str):
    return repositories.get_reviews_by_product(db, product_id)


def create_review(db: Session, user_id: str, product_id: str, rating: int, comment: Optional[str] = None):
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return repositories.create_review(db, user_id, product_id, rating, comment)


def get_product_variants(db: Session, product_id: str) -> list[models.ProductVariant]:
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return db.query(models.ProductVariant).filter(models.ProductVariant.product_id == product_id).order_by(models.ProductVariant.created_at).all()


def create_product_variant(db: Session, product_id: str, variant_data: dict) -> models.ProductVariant:
    product = repositories.get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")

    variant = models.ProductVariant(product_id=product_id, **variant_data)
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


def update_product_variant(db: Session, variant_id: str, variant_data: dict) -> models.ProductVariant:
    variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Variant not found")

    for key, value in variant_data.items():
        setattr(variant, key, value)

    db.commit()
    db.refresh(variant)
    return variant


def delete_product_variant(db: Session, variant_id: str):
    variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Variant not found")

    db.delete(variant)
    db.commit()
