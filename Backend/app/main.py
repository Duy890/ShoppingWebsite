from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.database import Base, engine, SessionLocal
from .core.config import ALLOWED_ORIGINS
from .core.rate_limit import limiter
from .controllers import router
from .core.security import hash_password
from .repositories import get_user_by_email, create_user
from .models import *
from .seed import run_seed
from .middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from .routes.system import router as system_router
from .routes.locations import router as locations_router
from .routes.navigation import router as navigation_router

app = FastAPI(title="e-shop. Backend API")
app.state.limiter = limiter

static_root = Path(__file__).resolve().parent / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(static_root)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

# Register exception handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(router)
app.include_router(system_router)
app.include_router(locations_router)
app.include_router(navigation_router)


ALLOWED_SCHEMA_COLUMNS = {
    "users": {"role"},
    "products": {
        "brand",
        "sku",
        "product_type",
        "rating",
        "review_count",
        "status",
        "view_count",
        "embedding",
    },
}


def add_column_if_missing(table_name: str, column_name: str, definition: str) -> None:
    if column_name not in ALLOWED_SCHEMA_COLUMNS.get(table_name, set()):
        raise ValueError("Invalid table/column for schema migration")
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
    return {
        "role": "role VARCHAR(255) NOT NULL DEFAULT 'user'",
        "brand": "brand VARCHAR(255)",
        "sku": "sku VARCHAR(255)",
        "product_type": "product_type VARCHAR(255)",
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
    add_column_if_missing("products", "product_type", definitions["product_type"])
    add_column_if_missing("products", "rating", definitions["rating"])
    add_column_if_missing("products", "review_count", definitions["review_count"])
    add_column_if_missing("products", "status", definitions["status"])
    add_column_if_missing("products", "view_count", definitions["view_count"])
    add_column_if_missing("products", "embedding", definitions["embedding"])


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
        run_seed(db)
    finally:
        db.close()
