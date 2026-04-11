from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .core.database import Base, engine, SessionLocal
from .controllers import router
from .core.security import hash_password
from .repositories import get_user_by_email, create_user
from .models import *

app = FastAPI(title="e-shop. Backend API")

static_root = Path(__file__).resolve().parent / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(static_root)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_column_if_missing(table_name: str, column_name: str, definition: str) -> None:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    if column_name in columns:
        return
    with engine.connect() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {definition}"))
        connection.commit()

def get_column_definitions() -> dict[str, str]:
    if engine.dialect.name == "sqlite":
        return {
            "role": "role TEXT NOT NULL DEFAULT 'user'",
            "brand": "brand TEXT",
            "sku": "sku TEXT",
            "rating": "rating REAL NOT NULL DEFAULT 0.0",
            "review_count": "review_count INTEGER NOT NULL DEFAULT 0",
            "status": "status TEXT NOT NULL DEFAULT 'active'",
            "view_count": "view_count INTEGER NOT NULL DEFAULT 0",
            "embedding": "embedding TEXT",
        }
    return {
        "role": "role VARCHAR(255) NOT NULL DEFAULT 'user'",
        "brand": "brand VARCHAR(255)",
        "sku": "sku VARCHAR(255)",
        "rating": "rating DOUBLE NOT NULL DEFAULT 0.0",
        "review_count": "review_count INT NOT NULL DEFAULT 0",
        "status": "status VARCHAR(255) NOT NULL DEFAULT 'active'",
        "view_count": "view_count INT NOT NULL DEFAULT 0",
        "embedding": "embedding JSON",
    }

def ensure_schema() -> None:
    definitions = get_column_definitions()
    add_column_if_missing("users", "role", definitions["role"])
    add_column_if_missing("products", "brand", definitions["brand"])
    add_column_if_missing("products", "sku", definitions["sku"])
    add_column_if_missing("products", "rating", definitions["rating"])
    add_column_if_missing("products", "review_count", definitions["review_count"])
    add_column_if_missing("products", "status", definitions["status"])
    add_column_if_missing("products", "view_count", definitions["view_count"])
    add_column_if_missing("products", "embedding", definitions["embedding"])

def get_or_create_category(db, name: str, description: str | None = None):
    category = db.query(Category).filter(Category.name == name).first()
    if category:
        return category
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_or_create_product(db, product_data: dict):
    product = db.query(Product).filter(Product.name == product_data["name"]).first()
    if product:
        # Update existing product with new high-end data if necessary
        for key, value in product_data.items():
            setattr(product, key, value)
        db.commit()
        return product
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def create_sample_data(db):
    if not get_user_by_email(db, "user@example.com"):
        create_user(
            db,
            email="user@example.com",
            hashed_password=hash_password("userpass"),
            full_name="Example User",
            role="user",
        )

    laptops = get_or_create_category(db, "Laptops", "High-performance portable computers.")
    phones = get_or_create_category(db, "Smartphones", "Next-gen mobile devices.")
    audio = get_or_create_category(db, "Audio", "Immersive sound and high-fidelity equipment.")

    # High-end Laptops
    get_or_create_product(db, {
        "name": "ZenBook Ultra 14 OLED",
        "description": "Ultrathin laptop with M3 Max equivalent performance and stunning OLED display.",
        "price": 45000000.0,
        "stock": 15,
        "category_id": laptops.id,
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?q=80&w=800&auto=format&fit=crop",
        "brand": "Asus",
        "sku": "ZB-ULTRA-01",
        "featured": True,
        "status": "active",
        "rating": 4.9,
        "review_count": 128,
        "view_count": 1205,
    })

    get_or_create_product(db, {
        "name": "MacBook Pro M3 Max",
        "description": "The most powerful MacBook ever, designed for creative professionals.",
        "price": 89000000.0,
        "stock": 8,
        "category_id": laptops.id,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=800&auto=format&fit=crop",
        "brand": "Apple",
        "sku": "MBP-M3-MAX",
        "featured": True,
        "status": "active",
        "rating": 5.0,
        "review_count": 245,
        "view_count": 3402,
    })

    # High-end Smartphones
    get_or_create_product(db, {
        "name": "iPhone 15 Pro Titanium",
        "description": "Forged in titanium, featuring the groundbreaking A17 Pro chip.",
        "price": 32000000.0,
        "stock": 25,
        "category_id": phones.id,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "brand": "Apple",
        "sku": "IPH-15-PRO",
        "featured": True,
        "status": "active",
        "rating": 4.8,
        "review_count": 512,
        "view_count": 8901,
    })

    get_or_create_product(db, {
        "name": "Samsung S24 Ultra",
        "description": "AI-powered smartphone with 200MP camera and built-in S Pen.",
        "price": 30000000.0,
        "stock": 30,
        "category_id": phones.id,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=800&auto=format&fit=crop",
        "brand": "Samsung",
        "sku": "SAM-S24-U",
        "featured": True,
        "status": "active",
        "rating": 4.7,
        "review_count": 420,
        "view_count": 5602,
    })

    # High-end Audio
    get_or_create_product(db, {
        "name": "Sony WH-1000XM5",
        "description": "Industry-leading noise cancelling wireless headphones with exceptional sound.",
        "price": 8500000.0,
        "stock": 50,
        "category_id": audio.id,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=800&auto=format&fit=crop",
        "brand": "Sony",
        "sku": "SONY-XM5",
        "featured": True,
        "status": "active",
        "rating": 4.9,
        "review_count": 890,
        "view_count": 12405,
    })

    get_or_create_product(db, {
        "name": "Bose QuietComfort Ultra",
        "description": "Bose’s most advanced noise cancelling earbuds yet, for immersive listening.",
        "price": 7500000.0,
        "stock": 40,
        "category_id": audio.id,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?q=80&w=800&auto=format&fit=crop",
        "brand": "Bose",
        "sku": "BOSE-QC-ULTRA",
        "featured": True,
        "status": "active",
        "rating": 4.8,
        "review_count": 310,
        "view_count": 4502,
    })

    get_or_create_product(db, {
        "name": "Pro Gaming Laptop G16",
        "description": "Unleash your gaming potential with RTX 4080 and 240Hz display.",
        "price": 55000000.0,
        "stock": 10,
        "category_id": laptops.id,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=800&auto=format&fit=crop",
        "brand": "ShopPro",
        "sku": "SP-GAME-G16",
        "featured": True,
        "status": "active",
        "rating": 4.6,
        "review_count": 85,
        "view_count": 2105,
    })

    get_or_create_product(db, {
        "name": "Studio Master Pro Headphones",
        "description": "Reference-grade open-back headphones for studio mixing and mastering.",
        "price": 12000000.0,
        "stock": 12,
        "category_id": audio.id,
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?q=80&w=800&auto=format&fit=crop",
        "brand": "AudioTech",
        "sku": "AT-STUDIO-PRO",
        "featured": True,
        "status": "active",
        "rating": 5.0,
        "review_count": 42,
        "view_count": 1502,
    })

ensure_schema()
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        if not get_user_by_email(db, "admin@example.com"):
            create_user(
                db,
                email="admin@example.com",
                hashed_password=hash_password("adminpass"),
                full_name="Admin User",
                role="admin",
            )
        create_sample_data(db)
    finally:
        db.close()

app.include_router(router)
