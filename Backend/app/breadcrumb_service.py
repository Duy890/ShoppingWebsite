import json
from sqlalchemy.orm import Session

from .models import Product, ProductVariant


def build_product_breadcrumbs(
    product: Product,
    variant: ProductVariant | None = None,
) -> list[dict]:
    breadcrumbs = []
    
    breadcrumbs.append({"name": "Trang chủ", "url": "/"})
    
    if product.product_type:
        breadcrumbs.append({
            "name": product.product_type,
            "url": f"/{slugify(product.product_type)}"
        })
    
    if product.brand:
        breadcrumbs.append({
            "name": product.brand,
            "url": f"/{slugify(product.product_type)}/{slugify(product.brand)}"
        })
    
    if product.product_line:
        breadcrumbs.append({
            "name": product.product_line,
            "url": f"/{slugify(product.product_type)}/{slugify(product.brand)}/{slugify(product.product_line)}"
        })
    
    if variant and variant.name:
        breadcrumbs.append({
            "name": variant.name,
            "url": None
        })
    
    return breadcrumbs


def build_product_type_breadcrumbs(product_type: str, brand: str | None = None) -> list[dict]:
    breadcrumbs = []
    
    breadcrumbs.append({"name": "Trang chủ", "url": "/"})
    breadcrumbs.append({
        "name": product_type,
        "url": f"/{slugify(product_type)}"
    })
    
    if brand:
        breadcrumbs.append({
            "name": brand,
            "url": f"/{slugify(product_type)}/{slugify(brand)}"
        })
    
    return breadcrumbs


def build_search_breadcrumbs(search_term: str) -> list[dict]:
    breadcrumbs = [
        {"name": "Trang chủ", "url": "/"},
        {"name": f'Tìm kiếm: "{search_term}"', "url": None}
    ]
    return breadcrumbs


def generate_breadcrumb_schema(breadcrumbs: list[dict], base_url: str = "") -> str:
    if not breadcrumbs:
        return ""
    
    items = []
    for i, crumb in enumerate(breadcrumbs):
        item = {
            "@type": "ListItem",
            "position": i + 1,
            "name": crumb["name"]
        }
        if crumb.get("url"):
            item["item"] = f"{base_url}{crumb['url']}"
        items.append(item)
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    return json.dumps(schema)


def slugify(text: str) -> str:
    if not text:
        return ""
    return text.lower().replace(" ", "-")