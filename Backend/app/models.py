import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(255), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    image_url = Column(Text, nullable=True)
    brand = Column(String(255), nullable=True)
    sku = Column(String(255), unique=True, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    status = Column(String(255), default="active")
    view_count = Column(Integer, default=0)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(255), default="pending")
    shipping_address = Column(Text, nullable=True)
    payment_method = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
