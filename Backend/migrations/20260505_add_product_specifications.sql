-- Product specifications system for FastAPI + SQLAlchemy deployments.
-- If you run the app against MySQL or PostgreSQL with the current SQLAlchemy models,
-- Base.metadata.create_all() creates the new tables automatically. Use this file
-- when you need an explicit manual migration in an existing database.

ALTER TABLE products ADD COLUMN product_type VARCHAR(255);

CREATE TABLE product_specifications (
  id VARCHAR(36) PRIMARY KEY,
  product_id VARCHAR(36) NOT NULL,
  group_name VARCHAR(255) NOT NULL,
  spec_key VARCHAR(255) NOT NULL,
  spec_value TEXT,
  display_order INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME,
  CONSTRAINT fk_product_specifications_product
    FOREIGN KEY (product_id) REFERENCES products(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_product_specifications_product_id
  ON product_specifications(product_id);

CREATE TABLE spec_templates (
  id VARCHAR(36) PRIMARY KEY,
  product_type VARCHAR(255) NOT NULL,
  group_name VARCHAR(255) NOT NULL,
  spec_key VARCHAR(255) NOT NULL,
  default_order INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_spec_templates_product_type
  ON spec_templates(product_type);
