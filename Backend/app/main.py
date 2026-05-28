from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.database import Base, engine, SessionLocal
from .core.config import settings
from .core.rate_limit import limiter
from .core.security import hash_password
from .repositories import get_user_by_email, create_user
from .models import *
from .seed import run_seed
from .state import maintenance_enabled
from .middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from .routes.system import router as system_router
from .routes.locations import router as locations_router
from .routes.navigation import router as navigation_router
from .routes.auth import router as auth_router
from .routes.products import router as products_router
from .routes.orders import router as orders_router
from .routes.cart import router as cart_router
from .routes.admin import router as admin_router
from .routes.chatbot import router as chatbot_router
from .routes.categories import router as categories_router
from .routes.uploads import router as uploads_router
from .routes.payment import router as payment_router
from .routes.addresses import router as addresses_router
from .routes.wishlist import router as wishlist_router
from .routes.recommendations import router as recommendations_router
from .routes.users import router as users_router

app = FastAPI(title="e-shop. Backend API")
app.state.limiter = limiter

static_root = Path(__file__).resolve().parent / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(static_root)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):
    allowed_paths = [
        "/api/system/health",
        "/api/system/maintenance",
        "/api/system/maintenance-status",
    ]
    if maintenance_enabled and request.url.path not in allowed_paths:
        return JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable. Under maintenance."},
        )
    return await call_next(request)

# Register exception handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers (domain modules)
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(cart_router)
app.include_router(admin_router)
app.include_router(chatbot_router)
app.include_router(categories_router)
app.include_router(uploads_router)
app.include_router(payment_router)
app.include_router(addresses_router)
app.include_router(wishlist_router)
app.include_router(recommendations_router)
app.include_router(users_router)
app.include_router(system_router)
app.include_router(locations_router)
app.include_router(navigation_router)


ALLOWED_SCHEMA_COLUMNS = {
    "users": {"role", "mfa_secret", "mfa_enabled", "last_login_at", "last_login_ip", "failed_login_attempts", "locked_until"},
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
    "product_specifications": {
        "unit",
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
        "mfa_secret": "mfa_secret TEXT NULL",
        "mfa_enabled": "mfa_enabled TINYINT(1) NOT NULL DEFAULT 0",
        "last_login_at": "last_login_at DATETIME NULL",
        "last_login_ip": "last_login_ip VARCHAR(45) NULL",
        "failed_login_attempts": "failed_login_attempts INT NOT NULL DEFAULT 0",
        "locked_until": "locked_until DATETIME NULL",
        "brand": "brand VARCHAR(255)",
        "sku": "sku VARCHAR(255)",
        "product_type": "product_type VARCHAR(255)",
        "rating": "rating DOUBLE NOT NULL DEFAULT 0.0",
        "review_count": "review_count INT NOT NULL DEFAULT 0",
        "status": "status VARCHAR(255) NOT NULL DEFAULT 'active'",
        "view_count": "view_count INT NOT NULL DEFAULT 0",
        "embedding": "embedding JSON",
        "unit": "unit VARCHAR(100) NULL",
    }

def ensure_schema() -> None:
    definitions = get_column_definitions()
    add_column_if_missing("users", "role", definitions["role"])
    add_column_if_missing("users", "mfa_secret", definitions["mfa_secret"])
    add_column_if_missing("users", "mfa_enabled", definitions["mfa_enabled"])
    add_column_if_missing("users", "last_login_at", definitions["last_login_at"])
    add_column_if_missing("users", "last_login_ip", definitions["last_login_ip"])
    add_column_if_missing("users", "failed_login_attempts", definitions["failed_login_attempts"])
    add_column_if_missing("users", "locked_until", definitions["locked_until"])
    add_column_if_missing("products", "brand", definitions["brand"])
    add_column_if_missing("products", "sku", definitions["sku"])
    add_column_if_missing("products", "product_type", definitions["product_type"])
    add_column_if_missing("products", "rating", definitions["rating"])
    add_column_if_missing("products", "review_count", definitions["review_count"])
    add_column_if_missing("products", "status", definitions["status"])
    add_column_if_missing("products", "view_count", definitions["view_count"])
    add_column_if_missing("products", "embedding", definitions["embedding"])
    add_column_if_missing("product_specifications", "unit", definitions["unit"])


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
