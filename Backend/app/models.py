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
    avatar_url = Column(Text, nullable=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(255), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=False)
    street = Column(Text, nullable=False)
    province = Column(String(255), nullable=False)
    district = Column(String(255), nullable=False)
    ward = Column(String(255), nullable=False)
    country = Column(String(255), default="Vietnam", nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="addresses")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True, index=True)
    level = Column(Integer, default=0)
    path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
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
    product_type = Column(String(255), nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    status = Column(String(255), default="active")
    view_count = Column(Integer, default=0)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    specifications = relationship("ProductSpecification", back_populates="product", cascade="all, delete-orphan")
    hotspots = relationship("ProductHotspot", back_populates="product", cascade="all, delete-orphan")
    related = relationship("RelatedProduct", foreign_keys="RelatedProduct.product_id", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    color_name = Column(String(255), nullable=True)
    color_code = Column(String(50), nullable=True)
    version_name = Column(String(255), nullable=True)
    ram = Column(String(255), nullable=True)
    storage = Column(String(255), nullable=True)
    sku = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    compare_price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    image_url = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    status = Column(String(255), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")


class RelatedProduct(Base):
    __tablename__ = "related_products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    related_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", foreign_keys=[product_id], back_populates="related")


class ProductHotspot(Base):
    __tablename__ = "product_hotspots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    type = Column(String(255), nullable=True)
    x_percent = Column(Float, nullable=False)
    y_percent = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="hotspots")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    group_name = Column(String(255), nullable=False)
    spec_key = Column(String(255), nullable=False)
    spec_value = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="specifications")


class SpecTemplate(Base):
    __tablename__ = "spec_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_type = Column(String(255), nullable=False, index=True)
    group_name = Column(String(255), nullable=False)
    spec_key = Column(String(255), nullable=False)
    default_order = Column(Integer, default=0, nullable=False)


class GpuBenchmark(Base):
    __tablename__ = "gpu_benchmarks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CpuBenchmark(Base):
    __tablename__ = "cpu_benchmarks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class GameRequirement(Base):
    __tablename__ = "game_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    game_name = Column(String(255), unique=True, nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    min_gpu_score = Column(Integer, nullable=False)
    recommended_gpu_score = Column(Integer, nullable=False)
    ultra_gpu_score = Column(Integer, nullable=False)
    min_cpu_score = Column(Integer, nullable=False)
    recommended_cpu_score = Column(Integer, nullable=False)
    ultra_cpu_score = Column(Integer, nullable=False)
    min_ram_gb = Column(Integer, nullable=False)
    recommended_ram_gb = Column(Integer, nullable=False)
    ultra_ram_gb = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


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
    variant_id = Column(String(36), ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(255), default="pending")
    shipping_address = Column(Text, nullable=True)
    payment_method = Column(String(255), nullable=True)
    address_id = Column(String(36), ForeignKey("addresses.id"), nullable=True)
    tracking_code = Column(String(255), nullable=True)
    shipping_provider = Column(String(255), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    variant_id = Column(String(36), ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    old_status = Column(String(255), nullable=True)
    new_status = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    changed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="status_history")
    changer = relationship("User")
