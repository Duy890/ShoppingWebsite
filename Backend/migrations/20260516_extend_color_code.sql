-- Extend product_variants.color_code from VARCHAR(7) to VARCHAR(50)
-- to support HEX, rgba(), transparent, and gradient values.

ALTER TABLE product_variants
  MODIFY COLUMN color_code VARCHAR(50) DEFAULT NULL;

-- Add new tables for extended product features
-- (auto-created by Base.metadata.create_all() on startup)

CREATE TABLE IF NOT EXISTS related_products (
  id VARCHAR(36) PRIMARY KEY,
  product_id VARCHAR(36) NOT NULL,
  related_product_id VARCHAR(36) NOT NULL,
  created_at DATETIME,
  INDEX idx_related_products_product_id (product_id)
);

CREATE TABLE IF NOT EXISTS product_hotspots (
  id VARCHAR(36) PRIMARY KEY,
  product_id VARCHAR(36) NOT NULL,
  label VARCHAR(255) NOT NULL,
  type VARCHAR(255),
  x_percent FLOAT NOT NULL,
  y_percent FLOAT NOT NULL,
  description TEXT,
  created_at DATETIME,
  INDEX idx_product_hotspots_product_id (product_id)
);

-- Add hierarchy columns to categories (if not already present)
ALTER TABLE categories
  ADD COLUMN IF NOT EXISTS slug VARCHAR(255) NOT NULL UNIQUE AFTER name,
  ADD COLUMN IF NOT EXISTS parent_id VARCHAR(36) DEFAULT NULL AFTER description,
  ADD COLUMN IF NOT EXISTS level INT DEFAULT 0 AFTER parent_id,
  ADD COLUMN IF NOT EXISTS path TEXT DEFAULT NULL AFTER level,
  ADD INDEX IF NOT EXISTS idx_categories_parent_id (parent_id),
  ADD INDEX IF NOT EXISTS idx_categories_slug (slug);
