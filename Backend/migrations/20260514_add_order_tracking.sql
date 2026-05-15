-- Migration: Add order tracking fields and status history table
-- Date: 2026-05-14
-- Description: Extend orders table with tracking fields and create order_status_history table

-- Add new columns to orders table
ALTER TABLE orders ADD COLUMN tracking_code VARCHAR(255);
ALTER TABLE orders ADD COLUMN shipping_provider VARCHAR(255);
ALTER TABLE orders ADD COLUMN estimated_delivery DATETIME;
ALTER TABLE orders ADD COLUMN delivered_at DATETIME;
ALTER TABLE orders ADD COLUMN cancelled_at DATETIME;
ALTER TABLE orders ADD COLUMN cancel_reason TEXT;
-- Create order_status_history table
CREATE TABLE order_status_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(36) NOT NULL,
    old_status VARCHAR(255),
    new_status VARCHAR(255) NOT NULL,
    note TEXT,
    changed_by VARCHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_order_status_history_order_id ON order_status_history(order_id);
CREATE INDEX idx_order_status_history_created_at ON order_status_history(created_at);