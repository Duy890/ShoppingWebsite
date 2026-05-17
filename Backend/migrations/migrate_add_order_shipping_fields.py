"""
Migration: Add shipping and order note fields to orders table.

Run this script to apply the migration:
    python migrate_add_order_shipping_fields.py

Or run the SQL directly in your database.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings


def migrate():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("orders")]

    migrations = []

    if "order_note" not in columns:
        migrations.append(
            "ALTER TABLE orders ADD COLUMN order_note TEXT NULL"
        )

    if "shipping_method" not in columns:
        migrations.append(
            "ALTER TABLE orders ADD COLUMN shipping_method VARCHAR(100) NULL"
        )

    if "shipping_fee" not in columns:
        migrations.append(
            "ALTER TABLE orders ADD COLUMN shipping_fee FLOAT DEFAULT 0"
        )

    if "estimated_delivery_days" not in columns:
        migrations.append(
            "ALTER TABLE orders ADD COLUMN estimated_delivery_days INTEGER NULL"
        )

    if not migrations:
        print("Migration already applied. No changes needed.")
        return

    with engine.connect() as conn:
        for sql in migrations:
            print(f"Executing: {sql}")
            conn.execute(text(sql))
        conn.commit()

    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()
