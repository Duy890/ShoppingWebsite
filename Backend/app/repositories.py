import uuid
from datetime import datetime
import re
import unicodedata

from sqlalchemy import extract, func, or_
from sqlalchemy.orm import joinedload, Session

from . import models


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_count(db: Session) -> int:
    return db.query(func.count(models.User.id)).scalar() or 0


def create_user(db: Session, email: str, hashed_password: str, full_name: str | None = None, role: str = "user") -> models.User:
    user = models.User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        is_admin=(role == "admin"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: models.User, full_name: str | None = None, avatar_url: str | None = None) -> models.User:
    if full_name is not None:
        user.full_name = full_name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_addresses_by_user(db: Session, user_id: str) -> list[models.Address]:
    return (
        db.query(models.Address)
        .filter(models.Address.user_id == user_id)
        .order_by(models.Address.is_default.desc(), models.Address.created_at.desc())
        .all()
    )


def get_address_by_id(db: Session, address_id: str) -> models.Address | None:
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def unset_default_addresses(db: Session, user_id: str) -> None:
    db.query(models.Address).filter(models.Address.user_id == user_id, models.Address.is_default == True).update({"is_default": False})


def create_address(db: Session, user_id: str, address_data: dict) -> models.Address:
    if address_data.get("is_default"):
        unset_default_addresses(db, user_id)
    elif not db.query(models.Address).filter(models.Address.user_id == user_id).first():
        address_data["is_default"] = True

    address = models.Address(user_id=user_id, **address_data)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def update_address(db: Session, address: models.Address, updates: dict) -> models.Address:
    if updates.get("is_default"):
        unset_default_addresses(db, address.user_id)

    for key, value in updates.items():
        if value is not None:
            setattr(address, key, value)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address: models.Address) -> None:
    user_id = address.user_id
    will_be_default = address.is_default
    db.delete(address)
    db.commit()

    if will_be_default:
        first_address = (
            db.query(models.Address)
            .filter(models.Address.user_id == user_id)
            .order_by(models.Address.created_at.desc())
            .first()
        )
        if first_address:
            first_address.is_default = True
            db.add(first_address)
            db.commit()


def set_default_address(db: Session, address: models.Address) -> models.Address:
    unset_default_addresses(db, address.user_id)
    address.is_default = True
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def get_categories(db: Session) -> list[models.Category]:
    return db.query(models.Category).order_by(models.Category.level, models.Category.name).all()


def get_categories_tree(db: Session) -> list[dict]:
    all_cats = db.query(models.Category).order_by(
        models.Category.level, models.Category.name
    ).all()

    nodes: dict[str, dict] = {}
    for cat in all_cats:
        nodes[cat.id] = {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "level": cat.level or 0,
            "parent_id": cat.parent_id,
            "children": [],
        }

    roots: list[dict] = []
    for cat in all_cats:
        node = nodes[cat.id]
        if cat.parent_id and cat.parent_id in nodes:
            nodes[cat.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


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


def get_search_suggestions(db: Session, query: str, limit: int = 8) -> list[dict]:
    if not query:
        return []

    search_value = f"%{query}%"
    product_matches = (
        db.query(models.Product)
        .filter(
            (models.Product.name.ilike(search_value)) |
            (models.Product.brand.ilike(search_value)) |
            (models.Product.description.ilike(search_value))
        )
        .order_by(models.Product.featured.desc(), models.Product.created_at.desc())
        .limit(limit)
        .all()
    )

    category_matches = (
        db.query(models.Category)
        .filter(models.Category.name.ilike(search_value))
        .order_by(models.Category.name)
        .limit(4)
        .all()
    )

    suggestions = []
    for product in product_matches:
        display_type = TYPE_MAPPING.get(product.product_type, product.product_type.capitalize() if product.product_type else "Sản phẩm")
        hierarchy = f"{display_type} > {product.brand}" if product.brand else display_type
        
        suggestions.append({
            "id": product.id,
            "type": "product",
            "label": product.name,
            "subtitle": hierarchy,
            "category": display_type,
            "image_url": product.image_url,
        })

    suggestions.extend([
        {
            "id": category.id,
            "type": "category",
            "label": category.name,
            "subtitle": category.description or "Browse category",
            "category": None,
            "image_url": None,
        }
        for category in category_matches
    ])

    return suggestions


def _slugify(text: str) -> str:
    """Convert Vietnamese text to a stable ASCII slug."""
    unicode_map = {
        "a": "àáâãäåāăạảấầẩẫậắằẳẵặ",
        "d": "đ",
        "e": "èéêëēĕẹẻẽếềểễệ",
        "i": "ìíîïīĭỉị",
        "o": "òóôõöōŏọỏốồổỗộớờởỡợ",
        "u": "ùúûüūŭụủứừửữự",
        "y": "ỳýỷỹỵ",
    }
    result = text.lower().strip()
    for ascii_char, unicode_chars in unicode_map.items():
        for unicode_char in unicode_chars:
            result = result.replace(unicode_char, ascii_char)
    result = unicodedata.normalize("NFD", result)
    result = re.sub(r"[\u0300-\u036f]", "", result)
    result = re.sub(r"[^a-z0-9\s-]", "", result)
    result = re.sub(r"[\s]+", "-", result.strip())
    return result or "category"


def create_category(
    db: Session,
    name: str,
    description: str | None = None,
    parent_id: str | None = None,
) -> models.Category:
    base_slug = _slugify(name)
    slug = base_slug
    counter = 1
    while db.query(models.Category).filter(models.Category.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    if parent_id:
        parent = db.query(models.Category).filter(models.Category.id == parent_id).first()
        if not parent:
            raise ValueError("Parent category not found")
        level = (parent.level or 0) + 1
        parent_path = parent.path or parent.slug or parent.id
        path = f"{parent_path}/{slug}"
    else:
        level = 0
        path = slug

    category = models.Category(
        name=name,
        description=description,
        slug=slug,
        parent_id=parent_id,
        level=level,
        path=path,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: str) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def delete_category(db: Session, category: models.Category) -> None:
    db.delete(category)
    db.commit()


def _get_all_category_ids(db: Session, category_id: str) -> list[str]:
    """Get a category and all its descendant category IDs recursively."""
    ids = [category_id]
    
    # Get direct children
    children = db.query(models.Category).filter(models.Category.parent_id == category_id).all()
    for child in children:
        ids.extend(_get_all_category_ids(db, child.id))
    
    return ids


def get_products(db: Session, category_id: str | None = None, search: str | None = None, featured: bool | None = None, sort_by: str | None = None, product_type: str | None = None, brand: str | None = None, page: int = 1, limit: int = 20) -> tuple[list[models.Product], int]:
    query = db.query(models.Product).options(joinedload(models.Product.category))

    if category_id:
        is_uuid = False
        try:
            uuid.UUID(category_id)
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            query = query.filter(models.Product.category_id == category_id)
        else:
            category = db.query(models.Category).filter(models.Category.slug == category_id).first()
            
            if category:
                all_category_ids = _get_all_category_ids(db, category.id)
                query = query.join(models.Category).filter(models.Category.id.in_(all_category_ids))
            else:
                query = query.filter(models.Product.id == None)

    if search:
        search_value = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(search_value),
                models.Product.brand.ilike(search_value),
                models.Product.sku.ilike(search_value),
                models.Product.description.ilike(search_value),
            )
        )
    if featured is not None:
        query = query.filter(models.Product.featured == featured)
    if product_type:
        query = query.filter(models.Product.product_type == product_type)
    if brand:
        query = query.filter(models.Product.brand.ilike(f"%{brand.strip()}%"))

    if sort_by:
        if sort_by == "price":
            query = query.order_by(models.Product.price)
        else:
            query = query.order_by(models.Product.created_at.desc())
    else:
        query = query.order_by(models.Product.created_at.desc())

    total = query.count()

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return items, total


def get_product(db: Session, product_id: str) -> models.Product | None:
    return (
        db.query(models.Product)
        .options(
            joinedload(models.Product.category),
            joinedload(models.Product.variants),
            joinedload(models.Product.specifications),
            joinedload(models.Product.product_images),
            joinedload(models.Product.reviews),
        )
        .filter(models.Product.id == product_id)
        .first()
    )


def get_product_images(db: Session, product_id: str):
    return (
        db.query(models.ProductImage)
        .filter(models.ProductImage.product_id == product_id)
        .order_by(models.ProductImage.sort_order)
        .all()
    )


def replace_product_images(db: Session, product_id: str, images: list[dict]):
    db.query(models.ProductImage).filter(models.ProductImage.product_id == product_id).delete()
    for i, img in enumerate(images):
        db.add(models.ProductImage(
            id=str(uuid.uuid4()),
            product_id=product_id,
            url=img["url"],
            alt_text=img.get("alt_text") or "",
            is_primary=img.get("is_primary", i == 0),
            sort_order=i,
        ))
    db.flush()


def increment_view_count(db: Session, product_id: str) -> None:
    db.query(models.Product).filter(
        models.Product.id == product_id
    ).update(
        {models.Product.view_count: models.Product.view_count + 1},
        synchronize_session=False,
    )
    db.commit()


def log_search(
    db: Session,
    query: str,
    user_id: str | None = None,
    results_count: int = 0,
) -> None:
    if not query or len(query.strip()) < 2:
        return
    entry = models.SearchLog(
        user_id=user_id,
        query=query.strip().lower(),
        results_count=results_count,
    )
    db.add(entry)
    db.commit()


def get_top_searches(db: Session, limit: int = 20) -> list[dict]:
    from sqlalchemy import func
    rows = (
        db.query(
            models.SearchLog.query,
            func.count(models.SearchLog.id).label("count"),
        )
        .filter(
            models.SearchLog.created_at >= datetime.utcnow().replace(
                hour=0, minute=0, second=0
            )
        )
        .group_by(models.SearchLog.query)
        .order_by(func.count(models.SearchLog.id).desc())
        .limit(limit)
        .all()
    )
    return [{"query": r.query, "count": r.count} for r in rows]


def get_brands_by_category(db: Session, category_id: str | None = None) -> list[str]:
    query = db.query(models.Product.brand).filter(models.Product.brand != None)

    if category_id:
        is_uuid = False
        try:
            uuid.UUID(category_id)
            is_uuid = True
        except ValueError:
            is_uuid = False

        if is_uuid:
            query = query.filter(models.Product.category_id == category_id)
        else:
            category = db.query(models.Category).filter(models.Category.slug == category_id).first()
            if category:
                all_category_ids = _get_all_category_ids(db, category.id)
                query = query.join(models.Category).filter(models.Category.id.in_(all_category_ids))
            else:
                return []

    brands = query.distinct().order_by(models.Product.brand).all()
    return [brand for (brand,) in brands if brand]


def create_product(db: Session, product_data: dict) -> models.Product:
    product = models.Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: models.Product, updates: dict) -> models.Product:
    for key, value in updates.items():
        if value is not None:
            setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product) -> None:
    db.delete(product)
    db.commit()


def get_product_specifications(db: Session, product_id: str) -> list[models.ProductSpecification]:
    return (
        db.query(models.ProductSpecification)
        .filter(models.ProductSpecification.product_id == product_id)
        .order_by(
            models.ProductSpecification.group_name,
            models.ProductSpecification.display_order,
            models.ProductSpecification.created_at,
        )
        .all()
    )


def create_product_specification(db: Session, product_id: str, spec_data: dict) -> models.ProductSpecification:
    spec = models.ProductSpecification(product_id=product_id, **spec_data)
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


def get_product_specification(db: Session, specification_id: str) -> models.ProductSpecification | None:
    return (
        db.query(models.ProductSpecification)
        .filter(models.ProductSpecification.id == specification_id)
        .first()
    )


def update_product_specification(db: Session, spec: models.ProductSpecification, updates: dict) -> models.ProductSpecification:
    for key, value in updates.items():
        if value is not None:
            setattr(spec, key, value)
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


def delete_product_specification(db: Session, spec: models.ProductSpecification) -> None:
    db.delete(spec)
    db.commit()


def replace_product_specifications(db: Session, product_id: str, specifications: list[dict]) -> list[models.ProductSpecification]:
    db.query(models.ProductSpecification).filter(models.ProductSpecification.product_id == product_id).delete()
    created_specs = [
        models.ProductSpecification(product_id=product_id, **spec_data)
        for spec_data in specifications
    ]
    db.add_all(created_specs)
    db.commit()
    for spec in created_specs:
        db.refresh(spec)
    return get_product_specifications(db, product_id)


def get_spec_templates(db: Session, product_type: str) -> list[models.SpecTemplate]:
    return (
        db.query(models.SpecTemplate)
        .filter(models.SpecTemplate.product_type == product_type)
        .order_by(models.SpecTemplate.group_name, models.SpecTemplate.default_order)
        .all()
    )


def get_all_spec_templates(db: Session) -> list[models.SpecTemplate]:
    return (
        db.query(models.SpecTemplate)
        .order_by(models.SpecTemplate.product_type, models.SpecTemplate.default_order)
        .all()
    )


def create_spec_template_with_check(db: Session, data: dict) -> models.SpecTemplate:
    existing = (
        db.query(models.SpecTemplate)
        .filter(
            models.SpecTemplate.product_type == data["product_type"],
            func.lower(models.SpecTemplate.group_name) == data["group_name"].strip().lower(),
            func.lower(models.SpecTemplate.spec_key)   == data["spec_key"].strip().lower(),
        )
        .first()
    )
    if existing:
        raise ValueError("Template with this product_type + group_name + spec_key already exists")

    tpl = models.SpecTemplate(
        id           = str(uuid.uuid4()),
        product_type = data["product_type"].strip(),
        group_name   = data["group_name"].strip(),
        spec_key     = data["spec_key"].strip(),
        default_order= data.get("default_order", 0),
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


def delete_spec_template(db: Session, template_id: str) -> None:
    tpl = db.query(models.SpecTemplate).filter(models.SpecTemplate.id == template_id).first()
    if not tpl:
        raise ValueError("Template not found")
    db.delete(tpl)
    db.commit()


def reorder_spec_templates(db: Session, product_type: str, ordered_ids: list[str]) -> None:
    for i, tid in enumerate(ordered_ids):
        db.query(models.SpecTemplate)\
          .filter(models.SpecTemplate.id == tid,
                  models.SpecTemplate.product_type == product_type)\
          .update({"default_order": i})
    db.commit()


def get_distinct_spec_template_types(db: Session) -> list[str]:
    rows = (
        db.query(models.SpecTemplate.product_type)
        .distinct()
        .order_by(models.SpecTemplate.product_type)
        .all()
    )
    return [r[0] for r in rows]


def delete_spec_template_type(db: Session, product_type: str) -> int:
    deleted = (
        db.query(models.SpecTemplate)
        .filter(models.SpecTemplate.product_type == product_type)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def get_reviews_by_product(db: Session, product_id: str) -> list[models.Review]:
    return (
        db.query(models.Review)
        .options(joinedload(models.Review.user))
        .filter(models.Review.product_id == product_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )


def create_review(db: Session, user_id: str, product_id: str, rating: int, comment: str | None) -> models.Review:
    existing = db.query(models.Review).filter(
        models.Review.user_id == user_id,
        models.Review.product_id == product_id
    ).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
        db.commit()
        db.refresh(existing)
        review = existing
    else:
        review = models.Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)

    # Update product rating and count
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        all_ratings = db.query(models.Review.rating).filter(models.Review.product_id == product_id).all()
        ratings = [r[0] for r in all_ratings]
        product.review_count = len(ratings)
        product.rating = sum(ratings) / len(ratings) if ratings else 0.0
        db.add(product)
        db.commit()

    return review


def get_wishlist(db: Session, user_id: str) -> list[models.Wishlist]:
    return (
        db.query(models.Wishlist)
        .options(joinedload(models.Wishlist.product))
        .filter(models.Wishlist.user_id == user_id)
        .order_by(models.Wishlist.created_at.desc())
        .all()
    )


def add_to_wishlist(db: Session, user_id: str, product_id: str) -> models.Wishlist:
    existing = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == user_id,
        models.Wishlist.product_id == product_id
    ).first()
    if existing:
        return existing
    item = models.Wishlist(user_id=user_id, product_id=product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_wishlist(db: Session, user_id: str, product_id: str) -> bool:
    item = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == user_id,
        models.Wishlist.product_id == product_id
    ).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def get_wishlist_product_ids(db: Session, user_id: str) -> list[str]:
    rows = db.query(models.Wishlist.product_id).filter(
        models.Wishlist.user_id == user_id
    ).all()
    return [r[0] for r in rows]


def get_or_create_cart(db: Session, user_id: str) -> models.Cart:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if cart:
        return cart

    cart = models.Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart_items(db: Session, user_id: str) -> list[models.CartItem]:
    cart = get_or_create_cart(db, user_id)
    return (
        db.query(models.CartItem)
        .options(joinedload(models.CartItem.product))
        .filter(models.CartItem.cart_id == cart.id)
        .all()
    )


def get_cart_item_by_id(db: Session, item_id: str) -> models.CartItem | None:
    return db.query(models.CartItem).options(joinedload(models.CartItem.product)).filter(models.CartItem.id == item_id).first()


def get_cart_item_by_product(db: Session, cart_id: str, product_id: str, variant_id: str | None = None) -> models.CartItem | None:
    query = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.product_id == product_id
    )
    if variant_id:
        query = query.filter(models.CartItem.variant_id == variant_id)
    else:
        query = query.filter(models.CartItem.variant_id.is_(None))
    return query.first()


def add_cart_item(db: Session, cart_id: str, product_id: str, quantity: int, variant_id: str | None = None) -> models.CartItem:
    cart_item = get_cart_item_by_product(db, cart_id, product_id, variant_id)
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, variant_id=variant_id)
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def update_cart_item(db: Session, item: models.CartItem, quantity: int) -> models.CartItem:
    item.quantity = quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_cart_item(db: Session, item: models.CartItem) -> None:
    db.delete(item)
    db.commit()


def clear_cart(db: Session, user_id: str) -> None:
    cart = get_or_create_cart(db, user_id)
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    db.commit()


def create_order(
    db: Session,
    user_id: str,
    total_amount: float,
    shipping_address: str | None,
    payment_method: str | None,
    address_id: str | None = None,
    shipping_method: str | None = None,
    shipping_fee: float = 0,
    order_note: str | None = None,
    estimated_delivery_days: int | None = None,
) -> models.Order:
    order = models.Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
        address_id=address_id,
        shipping_method=shipping_method,
        shipping_fee=shipping_fee,
        order_note=order_note,
        estimated_delivery_days=estimated_delivery_days,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def create_order_item(db: Session, order_id: str, product_id: str, quantity: int, price: float) -> models.OrderItem:
    item = models.OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_orders_by_user(db: Session, user_id: str) -> list[models.Order]:
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))
        .filter(models.Order.user_id == user_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: str) -> models.Order | None:
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))
        .filter(models.Order.id == order_id)
        .first()
    )


def get_all_orders(db: Session) -> list[models.Order]:
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product), joinedload(models.Order.user))
        .order_by(models.Order.created_at.desc())
        .all()
    )


def update_order_status(db: Session, order: models.Order, status: str) -> models.Order:
    order.status = status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_product_count(db: Session) -> int:
    return db.query(func.count(models.Product.id)).scalar() or 0


def get_order_count(db: Session) -> int:
    return db.query(func.count(models.Order.id)).scalar() or 0


def get_total_revenue(db: Session) -> float:
    return db.query(func.coalesce(func.sum(models.Order.total_amount), 0.0)).scalar() or 0.0


def get_revenue_by_month(db: Session) -> list[dict]:
    """Revenue for each month in the current year."""
    current_year = datetime.utcnow().year
    rows = (
        db.query(
            extract("month", models.Order.created_at).label("month_num"),
            func.coalesce(func.sum(models.Order.total_amount), 0.0).label("revenue"),
        )
        .filter(
            extract("year", models.Order.created_at) == current_year,
            models.Order.status.notin_(["cancelled", "payment_failed"]),
        )
        .group_by("month_num")
        .order_by("month_num")
        .all()
    )
    month_map = {int(row.month_num): float(row.revenue) for row in rows}
    return [
        {"month": f"T{month}", "revenue": month_map.get(month, 0.0)}
        for month in range(1, 13)
    ]


def get_revenue_by_year(db: Session) -> list[dict]:
    """Revenue for the latest five years."""
    current_year = datetime.utcnow().year
    rows = (
        db.query(
            extract("year", models.Order.created_at).label("year_num"),
            func.coalesce(func.sum(models.Order.total_amount), 0.0).label("revenue"),
        )
        .filter(
            extract("year", models.Order.created_at) >= current_year - 4,
            models.Order.status.notin_(["cancelled", "payment_failed"]),
        )
        .group_by("year_num")
        .order_by("year_num")
        .all()
    )
    year_map = {int(row.year_num): float(row.revenue) for row in rows}
    return [
        {"year": str(year), "revenue": year_map.get(year, 0.0)}
        for year in range(current_year - 4, current_year + 1)
    ]


def create_order_status_history(db: Session, order_id: str, old_status: str | None, new_status: str, note: str | None = None, changed_by: str | None = None) -> models.OrderStatusHistory:
    history = models.OrderStatusHistory(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        note=note,
        changed_by=changed_by
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_order_status_history(db: Session, order_id: str) -> list[models.OrderStatusHistory]:
    return db.query(models.OrderStatusHistory).filter(models.OrderStatusHistory.order_id == order_id).order_by(models.OrderStatusHistory.created_at).all()


# ---------------------------------------------------------------------------
# Refresh Tokens
# ---------------------------------------------------------------------------

def create_refresh_token(db: Session, user_id: str, token_hash: str, expires_at: datetime, device_info: str | None = None, ip_address: str | None = None) -> models.RefreshToken:
    rtoken = models.RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at,
    )
    db.add(rtoken)
    db.commit()
    db.refresh(rtoken)
    return rtoken


def get_refresh_token_by_hash(db: Session, token_hash: str) -> models.RefreshToken | None:
    return (
        db.query(models.RefreshToken)
        .filter(
            models.RefreshToken.token_hash == token_hash,
            models.RefreshToken.revoked.is_(False),
            models.RefreshToken.expires_at > datetime.utcnow(),
        )
        .first()
    )


def revoke_refresh_token(db: Session, token_id: str) -> None:
    db.query(models.RefreshToken).filter(models.RefreshToken.id == token_id).update({"revoked": True})
    db.commit()


def revoke_all_user_refresh_tokens(db: Session, user_id: str) -> None:
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.revoked.is_(False),
    ).update({"revoked": True})
    db.commit()


# ---------------------------------------------------------------------------
# MFA Challenges
# ---------------------------------------------------------------------------

def create_mfa_challenge(db: Session, user_id: str, jti: str, expires_at: datetime) -> models.MfaChallenge:
    challenge = models.MfaChallenge(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def get_mfa_challenge_by_jti(db: Session, jti: str) -> models.MfaChallenge | None:
    return (
        db.query(models.MfaChallenge)
        .filter(
            models.MfaChallenge.jti == jti,
            models.MfaChallenge.used.is_(False),
            models.MfaChallenge.expires_at > datetime.utcnow(),
        )
        .first()
    )


def mark_mfa_challenge_used(db: Session, jti: str) -> None:
    db.query(models.MfaChallenge).filter(models.MfaChallenge.jti == jti).update({"used": True})
    db.commit()


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------

def get_audit_logs(db: Session, limit: int = 100, offset: int = 0) -> list[models.AuditLog]:
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_audit_logs_for_user(db: Session, user_id: str, limit: int = 50, offset: int = 0) -> list[models.AuditLog]:
    return (
        db.query(models.AuditLog)
        .filter(models.AuditLog.user_id == user_id)
        .order_by(models.AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# Login History
# ---------------------------------------------------------------------------

def get_login_history(db: Session, user_id: str, limit: int = 20) -> list[models.LoginHistory]:
    return (
        db.query(models.LoginHistory)
        .filter(models.LoginHistory.user_id == user_id)
        .order_by(models.LoginHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def create_login_history(db: Session, user_id: str, success: bool, ip_address: str | None = None, user_agent: str | None = None, fail_reason: str | None = None) -> models.LoginHistory:
    entry = models.LoginHistory(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        fail_reason=fail_reason,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
