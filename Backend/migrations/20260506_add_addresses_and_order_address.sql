-- Migration: Add address management support and order address reference

CREATE TABLE IF NOT EXISTS addresses (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    street TEXT NOT NULL,
    district TEXT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id);

ALTER TABLE orders ADD COLUMN IF NOT EXISTS address_id TEXT;
CREATE INDEX IF NOT EXISTS idx_orders_address_id ON orders(address_id);
