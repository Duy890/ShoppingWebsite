import uuid
from datetime import datetime

from sqlalchemy import func, or_
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
    return db.query(models.Category).order_by(models.Category.name).all()


def get_categories_tree(db: Session) -> list[dict]:
    categories = get_categories(db)
    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "children": [],
        }
        for category in categories
    ]


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


def create_category(db: Session, name: str, description: str | None = None) -> models.Category:
    category = models.Category(name=name, description=description)
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


def get_products(db: Session, category_id: str | None = None, search: str | None = None, featured: bool | None = None, sort_by: str | None = None, product_type: str | None = None, brand: str | None = None) -> list[models.Product]:
    print(f"[DEBUG] get_products called with: category={category_id}, type={product_type}, brand={brand}")
    
    query = db.query(models.Product).options(joinedload(models.Product.category))

    if category_id:
        is_uuid = False
        try:
            uuid.UUID(category_id)
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            print(f"[DEBUG] Filtering by category ID: {category_id}")
            query = query.filter(models.Product.category_id == category_id)
        else:
            print(f"[DEBUG] Filtering by category slug: {category_id}")
            category = db.query(models.Category).filter(models.Category.slug == category_id).first()
            
            if category:
                print(f"[DEBUG] Found category: {category.name} (id={category.id})")
                all_category_ids = _get_all_category_ids(db, category.id)
                print(f"[DEBUG] All category IDs (including children): {all_category_ids}")
                print(f"[DEBUG] Product IDs in those categories: {db.query(models.Product.category_id).filter(models.Product.category_id.in_(all_category_ids)).all()}")
                query = query.join(models.Category).filter(models.Category.id.in_(all_category_ids))
            else:
                print(f"[DEBUG] Category slug '{category_id}' not found in database!")
                query = query.filter(models.Product.id == None)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if featured is not None:
        query = query.filter(models.Product.featured == featured)
    if product_type:
        query = query.filter(models.Product.product_type == product_type)
    if brand:
        query = query.filter(models.Product.brand.ilike(brand))

    if sort_by:
        if sort_by == "price":
            query = query.order_by(models.Product.price)
        else:
            query = query.order_by(models.Product.created_at.desc())
    else:
        query = query.order_by(models.Product.created_at.desc())

    return query.all()


def get_product(db: Session, product_id: str) -> models.Product | None:
    return db.query(models.Product).options(joinedload(models.Product.category)).filter(models.Product.id == product_id).first()


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


def get_spec_template(db: Session, product_type: str, group_name: str, spec_key: str) -> models.SpecTemplate | None:
    return (
        db.query(models.SpecTemplate)
        .filter(
            models.SpecTemplate.product_type == product_type,
            models.SpecTemplate.group_name == group_name,
            models.SpecTemplate.spec_key == spec_key,
        )
        .first()
    )


def create_spec_template(db: Session, product_type: str, group_name: str, spec_key: str, default_order: int) -> models.SpecTemplate:
    template = models.SpecTemplate(
        product_type=product_type,
        group_name=group_name,
        spec_key=spec_key,
        default_order=default_order,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_reviews_by_product(db: Session, product_id: str) -> list[models.Review]:
    return (
        db.query(models.Review)
        .options(joinedload(models.Review.user))
        .filter(models.Review.product_id == product_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )


def create_review(db: Session, user_id: str, product_id: str, rating: int, comment: str | None) -> models.Review:
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
        product.rating = sum(ratings) / len(ratings)
        db.add(product)
        db.commit()

    return review


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


def create_order(db: Session, user_id: str, total_amount: float, shipping_address: str | None, payment_method: str | None, address_id: str | None = None) -> models.Order:
    order = models.Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
        address_id=address_id,
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


def update_order_tracking(db: Session, order: models.Order, tracking_code: str | None = None, shipping_provider: str | None = None, estimated_delivery: datetime | None = None) -> models.Order:
    if tracking_code is not None:
        order.tracking_code = tracking_code
    if shipping_provider is not None:
        order.shipping_provider = shipping_provider
    if estimated_delivery is not None:
        order.estimated_delivery = estimated_delivery
    db.commit()
    db.refresh(order)
    return order
