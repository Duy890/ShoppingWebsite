from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

if settings.DATABASE_URL.startswith("sqlite"):
    raise ValueError(
        "SQLite is no longer supported. Configure DATABASE_URL for MySQL or PostgreSQL."
    )


def ensure_mysql_database_exists(database_url: str) -> None:
    url = make_url(database_url)
    if not url.drivername.startswith("mysql") or not url.database:
        return

    server_url = url.set(database=None)
    server_engine = create_engine(server_url, pool_pre_ping=True)
    try:
        server_engine.connect().execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{url.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
    finally:
        server_engine.dispose()


ensure_mysql_database_exists(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
