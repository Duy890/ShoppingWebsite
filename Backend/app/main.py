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

app = FastAPI(title="Shop Backend API")

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

    electronics = get_or_create_category(db, "Electronics", "Devices, gadgets, and accessories.")
    home = get_or_create_category(db, "Home & Garden", "Home decor, furniture, and essentials.")
    apparel = get_or_create_category(db, "Apparel", "Clothing, shoes, and accessories.")

    get_or_create_product(db, {
        "name": "Example Smart Watch",
        "description": "A stylish smart watch with fitness tracking and notifications.",
        "price": 199.99,
        "stock": 25,
        "category_id": electronics.id,
        "image_url": "https://via.placeholder.com/400x300.png?text=Smart+Watch",
        "brand": "ShopPro",
        "sku": "SP-WATCH-001",
        "featured": True,
        "status": "active",
        "rating": 4.5,
        "review_count": 12,
        "view_count": 102,
    })

    get_or_create_product(db, {
        "name": "Ceramic Vase",
        "description": "Handcrafted ceramic vase for home decoration.",
        "price": 34.99,
        "stock": 40,
        "category_id": home.id,
        "image_url": "https://via.placeholder.com/400x300.png?text=Ceramic+Vase",
        "brand": "HomeCraft",
        "sku": "HC-VASE-001",
        "featured": False,
        "status": "active",
        "rating": 4.2,
        "review_count": 8,
        "view_count": 46,
    })

    get_or_create_product(db, {
        "name": "Classic Denim Jacket",
        "description": "Comfortable denim jacket with timeless style.",
        "price": 79.99,
        "stock": 18,
        "category_id": apparel.id,
        "image_url": "https://via.placeholder.com/400x300.png?text=Denim+Jacket",
        "brand": "Fashionista",
        "sku": "FA-JACKET-001",
        "featured": False,
        "status": "active",
        "rating": 4.7,
        "review_count": 24,
        "view_count": 89,
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
