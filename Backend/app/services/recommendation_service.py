import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, repositories


def get_recommendations(
    db: Session,
    user_id: str | None = None,
    product_id: str | None = None,
    limit: int = 8,
) -> list[dict]:
    purchased_ids: set[str] = set()
    purchased_categories: set[str] = set()
    purchased_brands: set[str] = set()
    cart_product_ids: set[str] = set()
    wishlist_ids: set[str] = set()

    if user_id:
        orders = (
            db.query(models.OrderItem)
            .join(models.Order, models.Order.id == models.OrderItem.order_id)
            .join(models.Product, models.Product.id == models.OrderItem.product_id)
            .filter(
                models.Order.user_id == user_id,
                models.Order.status.notin_(["cancelled", "payment_failed"]),
            )
            .all()
        )
        for item in orders:
            purchased_ids.add(item.product_id)
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).first()
            if product:
                if product.category_id:
                    purchased_categories.add(product.category_id)
                if product.brand:
                    purchased_brands.add(product.brand.lower())

        cart = db.query(models.Cart).filter(
            models.Cart.user_id == user_id
        ).first()
        if cart:
            cart_items = db.query(models.CartItem).filter(
                models.CartItem.cart_id == cart.id
            ).all()
            cart_product_ids = {item.product_id for item in cart_items}

        wishlist_ids = set(
            repositories.get_wishlist_product_ids(db, user_id)
        )

    order_counts: dict[str, int] = {}
    rows = (
        db.query(
            models.OrderItem.product_id,
            func.count(models.OrderItem.id).label("cnt"),
        )
        .join(models.Order)
        .filter(models.Order.status.notin_(["cancelled", "payment_failed"]))
        .group_by(models.OrderItem.product_id)
        .all()
    )
    for r in rows:
        order_counts[r.product_id] = r.cnt

    cart_counts: dict[str, int] = {}
    rows = (
        db.query(
            models.CartItem.product_id,
            func.count(models.CartItem.id).label("cnt"),
        )
        .group_by(models.CartItem.product_id)
        .all()
    )
    for r in rows:
        cart_counts[r.product_id] = r.cnt

    products = (
        db.query(models.Product)
        .filter(
            models.Product.status == "active",
            models.Product.stock > 0,
        )
        .all()
    )

    scored: list[tuple[float, models.Product]] = []

    for product in products:
        if product_id and product.id == product_id:
            continue
        if product.id in purchased_ids:
            continue

        view_score = math.log(max(product.view_count or 0, 0) + 1)
        order_score = order_counts.get(product.id, 0) * 3.0
        cart_score = cart_counts.get(product.id, 0) * 1.5
        rating_score = (product.rating or 0) * 1.0
        popularity = view_score + order_score + cart_score + rating_score

        personal = 0.0
        if product.category_id in purchased_categories:
            personal += 5.0
        if product.brand and product.brand.lower() in purchased_brands:
            personal += 3.0
        if product.id in wishlist_ids:
            personal += 2.0

        abandoned = 4.0 if product.id in cart_product_ids else 0.0

        final_score = popularity + personal + abandoned

        if not user_id:
            final_score = popularity

        scored.append((final_score, product))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_products = [p for _, p in scored[:limit]]

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image_url": p.image_url,
            "brand": p.brand,
            "rating": p.rating,
            "review_count": p.review_count,
            "product_type": p.product_type,
            "category_id": p.category_id,
        }
        for p in top_products
    ]


def get_similar_products(
    db: Session,
    product_id: str,
    limit: int = 6,
) -> list[dict]:
    source = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not source:
        return []

    products = (
        db.query(models.Product)
        .filter(
            models.Product.status == "active",
            models.Product.stock > 0,
            models.Product.id != product_id,
        )
        .all()
    )

    scored = []
    for p in products:
        score = 0.0
        if source.category_id and p.category_id == source.category_id:
            score += 5.0
        if source.brand and p.brand and p.brand.lower() == source.brand.lower():
            score += 3.0
        if source.product_type and p.product_type == source.product_type:
            score += 2.0
        if source.price:
            price_ratio = p.price / source.price
            if 0.7 <= price_ratio <= 1.3:
                score += 2.0
        score += (p.rating or 0) * 0.5
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for _, p in scored[:limit]]
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image_url": p.image_url,
            "brand": p.brand,
            "rating": p.rating,
            "review_count": p.review_count,
            "product_type": p.product_type,
        }
        for p in top
    ]


def get_cart_recommendations(
    db: Session,
    user_id: str,
    limit: int = 4,
) -> list[dict]:
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()
    if not cart:
        return []

    cart_items = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).all()
    if not cart_items:
        return []

    cart_pids = {item.product_id for item in cart_items}

    co_purchased: dict[str, int] = {}
    for pid in cart_pids:
        order_ids = (
            db.query(models.OrderItem.order_id)
            .filter(models.OrderItem.product_id == pid)
            .subquery()
        )
        rows = (
            db.query(
                models.OrderItem.product_id,
                func.count(models.OrderItem.id).label("cnt"),
            )
            .filter(
                models.OrderItem.order_id.in_(order_ids),
                models.OrderItem.product_id.notin_(cart_pids),
            )
            .group_by(models.OrderItem.product_id)
            .all()
        )
        for r in rows:
            co_purchased[r.product_id] = (
                co_purchased.get(r.product_id, 0) + r.cnt
            )

    if co_purchased:
        top_pids = sorted(
            co_purchased, key=lambda pid: co_purchased[pid], reverse=True
        )[:limit]
        products = (
            db.query(models.Product)
            .filter(
                models.Product.id.in_(top_pids),
                models.Product.status == "active",
                models.Product.stock > 0,
            )
            .all()
        )
        if products:
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "image_url": p.image_url,
                    "brand": p.brand,
                    "rating": p.rating,
                }
                for p in products[:limit]
            ]

    category_ids = set()
    for pid in cart_pids:
        p = db.query(models.Product).filter(models.Product.id == pid).first()
        if p and p.category_id:
            category_ids.add(p.category_id)

    fallback = (
        db.query(models.Product)
        .filter(
            models.Product.category_id.in_(category_ids),
            models.Product.id.notin_(cart_pids),
            models.Product.status == "active",
            models.Product.stock > 0,
        )
        .order_by(models.Product.view_count.desc(), models.Product.rating.desc())
        .limit(limit)
        .all()
    )
    return [
        {"id": p.id, "name": p.name, "price": p.price,
         "image_url": p.image_url, "brand": p.brand, "rating": p.rating}
        for p in fallback
    ]
