from sqlalchemy import func
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


def update_user_profile(db: Session, user: models.User, full_name: str | None = None) -> models.User:
    if full_name is not None:
        user.full_name = full_name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_categories(db: Session) -> list[models.Category]:
    return db.query(models.Category).order_by(models.Category.name).all()


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


def get_products(db: Session, category_id: str | None = None, search: str | None = None, featured: bool | None = None, sort_by: str | None = None) -> list[models.Product]:
    query = db.query(models.Product).options(joinedload(models.Product.category))

    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if featured is not None:
        query = query.filter(models.Product.featured == featured)

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


def get_cart_item_by_product(db: Session, cart_id: str, product_id: str) -> models.CartItem | None:
    return (
        db.query(models.CartItem)
        .filter(models.CartItem.cart_id == cart_id, models.CartItem.product_id == product_id)
        .first()
    )


def add_cart_item(db: Session, cart_id: str, product_id: str, quantity: int) -> models.CartItem:
    cart_item = get_cart_item_by_product(db, cart_id, product_id)
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
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


def create_order(db: Session, user_id: str, total_amount: float, shipping_address: str | None, payment_method: str | None) -> models.Order:
    order = models.Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
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
