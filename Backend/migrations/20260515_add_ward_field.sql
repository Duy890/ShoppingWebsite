-- Add ward field to addresses table
ALTER TABLE addresses ADD COLUMN ward VARCHAR(255) NULLABLE AFTER district;

-- Rename city to province for clarity (if needed in future)
-- ALTER TABLE addresses CHANGE COLUMN city province VARCHAR(255) NOT NULL;
