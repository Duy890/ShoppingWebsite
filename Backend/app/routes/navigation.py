from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import Product
from .. import models
from typing import List, Dict

router = APIRouter(prefix="/navigation", tags=["navigation"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/debug-categories")
async def debug_categories(db: Session = Depends(get_db)):
    """
    Debug endpoint to list all available categories and their slugs.
    """
    categories = db.query(models.Category).order_by(models.Category.level, models.Category.name).all()
    return {
        "count": len(categories),
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "parent_id": c.parent_id,
                "level": c.level
            }
            for c in categories
        ]
    }

@router.get("/debug-products")
async def debug_products(db: Session = Depends(get_db)):
    """
    Debug endpoint to check product category assignments.
    """
    products = db.query(Product).limit(10).all()
    categories = {c.id: c.name for c in db.query(models.Category).all()}
    return {
        "sample_products": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "product_type": p.product_type,
                "category_id": p.category_id,
                "category_name": categories.get(p.category_id, "N/A")
            }
            for p in products
        ]
    }

# Mapping internal product_type to display name
TYPE_MAPPING = {
    "phone": "Điện thoại",
    "laptop": "Laptop",
    "tablet": "Máy tính bảng",
    "watch": "Đồng hồ thông minh",
    "audio": "Tai nghe",
    "keyboard": "Bàn phím",
    "mouse": "Chuột",
    "monitor": "Màn hình",
    "pc": "PC",
    "accessory": "Phụ kiện"
}

@router.get("/tree")
async def get_navigation_tree(db: Session = Depends(get_db)):
    """
    Returns the full hierarchical category tree.
    """
    # Fetch all categories
    categories = db.query(models.Category).all()
    
    # Build a map for easy lookup
    cat_map = {}
    for cat in categories:
        cat_map[cat.id] = {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "level": cat.level,
            "children": []
        }
    
    tree = []
    for cat in categories:
        node = cat_map[cat.id]
        if cat.parent_id:
            parent = cat_map.get(cat.parent_id)
            if parent:
                parent["children"].append(node)
        else:
            # Level 0 categories
            tree.append(node)
            
    # Sort children by name
    def sort_tree(nodes):
        nodes.sort(key=lambda x: x["name"])
        for node in nodes:
            if node["children"]:
                sort_tree(node["children"])
                
    sort_tree(tree)
    
    # Override sort for top level to maintain preferred order
    preferred_order = [
        "Điện thoại", "Laptop", "Máy tính bảng", "Âm thanh", "Đồng hồ", "Phụ kiện", "Gaming", "PC", "Thiết bị mạng"
    ]
    
    order_map = {name: i for i, name in enumerate(preferred_order)}
    tree.sort(key=lambda x: order_map.get(x["name"], 999))
    
    return tree


@router.get("/categories")
async def get_navigation_categories(db: Session = Depends(get_db)):
    """
    Returns a grouped list of product types and their associated brands.
    Used for the mega menu navigation.
    """
    # Query distinct product_type and brand from products
    # We only want active products if there's a status field (there is: Product.status)
    results = db.query(Product.product_type, Product.brand).filter(Product.status == "active").distinct().all()
    
    # Group brands by product_type
    nav_data = {}
    for p_type, brand in results:
        if not p_type or not brand:
            continue
        
        display_name = TYPE_MAPPING.get(p_type, p_type.capitalize())
        
        if display_name not in nav_data:
            nav_data[display_name] = {
                "product_type": display_name,
                "type_slug": p_type,
                "brands": set()
            }
        
        nav_data[display_name]["brands"].add(brand)
    
    # Convert sets to sorted lists
    final_data = []
    # Maintain a preferred order for product types as requested
    preferred_order = [
        "Điện thoại", "Laptop", "Máy tính bảng", "Đồng hồ thông minh", 
        "Tai nghe", "Bàn phím", "Chuột", "Màn hình", "PC", "Phụ kiện"
    ]
    
    # First add products in preferred order
    for p_type in preferred_order:
        if p_type in nav_data:
            item = nav_data.pop(p_type)
            item["brands"] = sorted(list(item["brands"]))
            final_data.append(item)
            
    # Add any remaining product types
    for p_type in sorted(nav_data.keys()):
        item = nav_data[p_type]
        item["brands"] = sorted(list(item["brands"]))
        final_data.append(item)
        
    return final_data
